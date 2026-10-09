"""Station autocomplete: Navitia when a token is configured, static list otherwise."""
from __future__ import annotations

import json
from pathlib import Path

import requests

from domain.planner import norm

# Every station of the Open Data `tgvmax` dataset (origins and destinations), under its exact name.
with open(Path(__file__).with_name("stations.json"), encoding="utf-8") as _f:
    STATIONS: list[str] = json.load(_f)


def search_stations(q: str, token: str = "", base_url: str = "") -> list[str]:
    q = q.strip()
    if token and q:
        try:
            r = requests.get(
                f"{base_url}/places",
                params={"q": q, "type[]": "stop_area", "count": 10},
                auth=(token, ""),
                timeout=8,
            )
            r.raise_for_status()
            names = [p["name"] for p in r.json().get("places", [])]
            if names:
                return names
        except (requests.RequestException, ValueError, KeyError):
            pass  # fall back to the static list
    nq = norm(q)
    return [s for s in STATIONS if nq in norm(s)][:15] if nq else STATIONS[:15]
