import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.opendata_client import parse_rows  # noqa: E402


def row(no, card, dep="08:00"):
    return {"date": "2026-10-10", "train_no": no, "origine": "STRASBOURG", "destination": "PARIS (intramuros)",
            "heure_depart": dep, "heure_arrivee": "10:10", "od_happy_card": card}


def test_only_max_trains_kept_and_deduplicated():
    trains = parse_rows([row("1", "OUI"), row("1", "OUI"), row("2", "NON"), row("3", None)])
    assert [t.no for t in trains] == ["1"]
