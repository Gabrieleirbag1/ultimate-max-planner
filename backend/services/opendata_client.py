"""Availability of 0 EUR TGV MAX seats, from the SNCF Open Data `tgvmax` dataset."""
from __future__ import annotations

import threading
import time as _time
from datetime import date, timedelta

import requests

from domain.models import Train
from domain.planner import make_train

FIELDS = "date,train_no,origine,destination,heure_depart,heure_arrivee,od_happy_card"

_cache: dict[tuple[str, str], tuple[float, list[Train]]] = {}
_lock = threading.Lock()


class OpenDataError(RuntimeError):
    pass


def parse_rows(rows: list[dict]) -> list[Train]:
    """Keep only genuine 0 EUR (MAX) trains, de-duplicated; every leg of any itinerary comes from here."""
    trains: dict[tuple, Train] = {}  # the dataset contains repeated records
    for r in rows:
        if r.get("od_happy_card") != "OUI":
            continue  # not available with a MAX pass
        try:
            day = date.fromisoformat(r["date"][:10])
            t = make_train(
                str(r["train_no"]), r["origine"], r["destination"], day,
                r["heure_depart"], r["heure_arrivee"],
            )
            trains[(t.no, t.origin, t.destination, t.dep)] = t
        except (KeyError, TypeError, ValueError):
            continue  # skip malformed record
    return list(trains.values())


def fetch_trains(url: str, date_from: date, date_to: date, ttl: int) -> list[Train]:
    """All MAX-available direct trains with departure in [date_from, date_to]."""
    key = (date_from.isoformat(), date_to.isoformat())
    with _lock:
        hit = _cache.get(key)
        if hit and _time.time() - hit[0] < ttl:
            return hit[1]

    where = (
        f'od_happy_card="OUI" AND date>=date\'{date_from.isoformat()}\' '
        f"AND date<=date'{date_to.isoformat()}'"
    )
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            resp = requests.get(url, params={"where": where, "select": FIELDS}, timeout=60)
            resp.raise_for_status()
            rows = resp.json()
            break
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            _time.sleep(1 + attempt)
    else:
        raise OpenDataError(f"SNCF Open Data indisponible: {last_exc}")

    trains = parse_rows(rows)

    with _lock:
        _cache[key] = (_time.time(), trains)
    return trains
