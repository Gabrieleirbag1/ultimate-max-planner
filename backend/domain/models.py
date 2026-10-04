from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Train:
    """One direct TGV MAX train (a record of the SNCF `tgvmax` dataset)."""

    no: str
    origin: str
    destination: str
    dep: datetime
    arr: datetime
    o_node: str
    d_node: str

    def to_dict(self) -> dict:
        return {
            "train_no": self.no,
            "origin": self.origin,
            "destination": self.destination,
            "dep": self.dep.isoformat(timespec="minutes"),
            "arr": self.arr.isoformat(timespec="minutes"),
        }


@dataclass(frozen=True)
class Itinerary:
    legs: tuple[Train, ...]
    date: str  # anchor day (day of the last departure)
    overnight: bool = False
    stay_city: str | None = None

    @property
    def dep(self) -> datetime:
        return self.legs[0].dep

    @property
    def arr(self) -> datetime:
        return self.legs[-1].arr

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "origin_date": self.dep.date().isoformat(),
            "dep": self.dep.isoformat(timespec="minutes"),
            "arr": self.arr.isoformat(timespec="minutes"),
            "duration_min": int((self.arr - self.dep).total_seconds() // 60),
            "transfers": len(self.legs) - 1,
            "overnight": self.overnight,
            "stay_city": self.stay_city,
            "legs": [leg.to_dict() for leg in self.legs],
        }
