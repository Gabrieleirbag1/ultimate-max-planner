import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.planner import Planner, make_train  # noqa: E402

D = date(2026, 10, 10)
PREV = date(2026, 10, 9)


def t(no, o, d, dep, arr, day=D):
    return make_train(no, o, d, day, dep, arr)


def test_direct():
    p = Planner([t("1", "STRASBOURG", "BORDEAUX ST JEAN", "08:00", "15:00")])
    r = p.find("Strasbourg", "Bordeaux", D)
    assert len(r) == 1 and len(r[0].legs) == 1


def test_connection_via_paris():
    p = Planner([
        t("1", "STRASBOURG", "PARIS (intramuros)", "06:00", "08:10"),
        t("2", "PARIS (intramuros)", "BORDEAUX ST JEAN", "09:30", "11:50"),
    ])
    r = p.find("Strasbourg", "Bordeaux", D)
    assert [len(i.legs) for i in r] == [2]


def test_min_connection_rejected():
    p = Planner([
        t("1", "STRASBOURG", "MASSY TGV", "06:00", "08:10"),
        t("2", "MASSY TGV", "BORDEAUX ST JEAN", "08:20", "11:00"),
    ])
    assert p.find("Strasbourg", "Bordeaux", D) == []


def test_paris_transfer_needs_75min():
    p = Planner([
        t("1", "STRASBOURG", "PARIS (intramuros)", "06:00", "08:10"),
        t("2", "PARIS (intramuros)", "BORDEAUX ST JEAN", "09:10", "11:50"),  # 60 min: too short
        t("3", "PARIS (intramuros)", "BORDEAUX ST JEAN", "09:30", "12:20"),  # 80 min: ok
    ])
    r = p.find("Strasbourg", "Bordeaux", D)
    assert [i.legs[-1].no for i in r] == ["3"]


def test_past_trains_ignored():
    trains = [
        t("1", "STRASBOURG", "BORDEAUX ST JEAN", "06:00", "13:00"),
        t("2", "STRASBOURG", "BORDEAUX ST JEAN", "18:00", "23:00"),
    ]
    r = Planner(trains, now=datetime(2026, 10, 10, 12, 0)).find("Strasbourg", "Bordeaux", D)
    assert [i.legs[0].no for i in r] == ["2"]


def test_custom_hub_nancy():
    trains = [
        t("1", "STRASBOURG", "NANCY", "06:00", "07:00"),
        t("2", "NANCY", "PARIS (intramuros)", "07:30", "09:15"),
        t("3", "PARIS (intramuros)", "BORDEAUX ST JEAN", "10:30", "13:20"),
    ]
    assert Planner(trains).find("Strasbourg", "Bordeaux", D) == []
    r = Planner(trains).find("Strasbourg", "Bordeaux", D, hubs=["Nancy"])
    assert len(r) == 1 and len(r[0].legs) == 3


def test_overnight():
    trains = [
        t("1", "PARIS (intramuros)", "STRASBOURG", "19:00", "21:10", PREV),
        t("2", "STRASBOURG", "BORDEAUX ST JEAN", "07:00", "14:00"),
    ]
    p = Planner(trains)
    assert p.find("Paris", "Bordeaux", D, hubs=["Strasbourg"]) == []
    r = p.find("Paris", "Bordeaux", D, hubs=["Strasbourg"], overnight=True)
    assert len(r) == 1 and r[0].overnight and r[0].stay_city == "STRASBOURG"
    assert r[0].to_dict()["origin_date"] == PREV.isoformat()
