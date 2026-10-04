"""Connection / overnight itinerary search over direct TGV MAX trains."""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Callable, Iterable, Iterator

from .models import Itinerary, Train

# Aliases matched against normalized station names (word-boundary containment).
DEFAULT_HUBS = ["PARIS", "MASSY", "MARNE LA VALLEE", "CDG"]

MIN_CONNECTION = timedelta(minutes=30)
# The dataset only says "PARIS (intramuros)": Est/Lyon/Montparnasse... are indistinguishable,
# so any Paris connection is assumed to be a station change.
MIN_PARIS_TRANSFER = timedelta(minutes=75)
MAX_JOURNEY_SPAN = timedelta(hours=18)
MIN_SLEEP = timedelta(hours=4)
EVENING_START = time(17, 0)
MORNING_START = time(5, 0)
MAX_RESULTS_PER_DAY = 40


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", s).strip()


def node_of(station: str) -> str:
    """Stations of the Paris group are interchangeable nodes (with a longer transfer)."""
    n = norm(station)
    return "PARIS" if n.startswith("PARIS") else n


def matcher(queries: Iterable[str]) -> Callable[[str], bool]:
    qs = [f" {norm(q)} " for q in queries if norm(q)]

    def match(station: str) -> bool:
        padded = f" {norm(station)} "
        return any(q in padded for q in qs)

    return match


def make_train(no: str, origin: str, destination: str, day: date, dep_hm: str, arr_hm: str) -> Train:
    dep = datetime.combine(day, time.fromisoformat(dep_hm))
    arr = datetime.combine(day, time.fromisoformat(arr_hm))
    if arr <= dep:  # arrival after midnight
        arr += timedelta(days=1)
    return Train(no, origin, destination, dep, arr, node_of(origin), node_of(destination))


def _min_connection(prev: Train, nxt: Train) -> timedelta:
    if prev.d_node == "PARIS":
        return MIN_PARIS_TRANSFER
    return MIN_CONNECTION


class Planner:
    def __init__(self, trains: Iterable[Train], now: datetime | None = None):
        """`now`: trains that already left are ignored."""
        if now is not None:
            trains = [t for t in trains if t.dep >= now]
        self.by_date: dict[date, list[Train]] = defaultdict(list)
        self.idx: dict[date, dict[str, list[Train]]] = defaultdict(lambda: defaultdict(list))
        for t in sorted(trains, key=lambda t: t.dep):
            d = t.dep.date()
            self.by_date[d].append(t)
            self.idx[d][t.o_node].append(t)

    # -- exploration ------------------------------------------------------
    def _explore(
        self,
        day: date,
        start: Callable[[Train], bool],
        earliest: time,
        max_legs: int,
        is_hub: Callable[[str], bool],
        is_dest: Callable[[str], bool],
    ) -> Iterator[list[Train]]:
        """Yield every chain of trains departing on `day`, starting where `start`
        accepts, stopping at the destination and only transiting through hubs."""

        def rec(chain: list[Train], visited: set[str]) -> Iterator[list[Train]]:
            yield chain
            last = chain[-1]
            if len(chain) >= max_legs or is_dest(last.destination) or not is_hub(last.destination):
                return
            for t in self.idx[day].get(last.d_node, ()):
                if t.dep < last.arr + _min_connection(last, t) or t.d_node in visited:
                    continue
                if t.arr - chain[0].dep > MAX_JOURNEY_SPAN:
                    continue
                yield from rec(chain + [t], visited | {t.d_node})

        for first in self.by_date.get(day, ()):
            if first.dep.time() >= earliest and start(first):
                yield from rec([first], {first.o_node, first.d_node})

    # -- public search ----------------------------------------------------
    def find(
        self,
        origin: str,
        destination: str,
        day: date,
        hubs: Iterable[str] = (),
        max_legs: int = 3,
        overnight: bool = False,
    ) -> list[Itinerary]:
        is_origin = matcher([origin])
        is_dest = matcher([destination])
        is_hub = matcher([*DEFAULT_HUBS, *hubs])
        results: list[Itinerary] = []

        for chain in self._explore(day, lambda t: is_origin(t.origin), time(0, 0), max_legs, is_hub, is_dest):
            if is_dest(chain[-1].destination):
                results.append(Itinerary(tuple(chain), day.isoformat()))

        if overnight and max_legs >= 2:
            prev = day - timedelta(days=1)
            for part1 in self._explore(
                prev, lambda t: is_origin(t.origin), EVENING_START, max_legs - 1, is_hub, is_dest
            ):
                stay = part1[-1]
                if is_dest(stay.destination) or not is_hub(stay.destination):
                    continue
                for part2 in self._explore(
                    day,
                    lambda t, n=stay.d_node: t.o_node == n and t.dep >= stay.arr + MIN_SLEEP,
                    MORNING_START,
                    max_legs - len(part1),
                    is_hub,
                    is_dest,
                ):
                    if is_dest(part2[-1].destination):
                        results.append(
                            Itinerary(tuple(part1 + part2), day.isoformat(), True, stay.destination)
                        )

        results.sort(key=lambda i: (i.arr, len(i.legs), i.dep))
        return results[:MAX_RESULTS_PER_DAY]

    def summarize(self, itineraries: list[Itinerary]) -> dict | None:
        if not itineraries:
            return None
        best = min(itineraries, key=lambda i: (i.arr, len(i.legs)))
        return {
            "count": len(itineraries),
            "direct": any(len(i.legs) == 1 for i in itineraries),
            "has_overnight": any(i.overnight for i in itineraries),
            "best": {"dep": best.dep.isoformat(timespec="minutes"), "arr": best.arr.isoformat(timespec="minutes")},
        }
