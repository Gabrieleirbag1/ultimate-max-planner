"""Station autocomplete: Navitia when a token is configured, static list otherwise."""
from __future__ import annotations

import requests

from domain.planner import norm

# Common TGV stations; names follow the vocabulary of the Open Data dataset.
STATIONS = [
    "PARIS (intramuros)", "MASSY TGV", "MARNE LA VALLEE CHESSY", "AEROPORT CDG2 TGV",
    "STRASBOURG", "MULHOUSE VILLE", "COLMAR", "NANCY", "METZ VILLE", "LILLE EUROPE", "LILLE FLANDRES",
    "LYON PART DIEU", "LYON ST EXUPERY TGV", "MARSEILLE ST CHARLES", "AIX EN PROVENCE TGV", "AVIGNON TGV",
    "MONTPELLIER ST ROCH", "NIMES", "PERPIGNAN", "TOULOUSE MATABIAU", "BORDEAUX ST JEAN", "BIARRITZ",
    "BAYONNE", "HENDAYE", "LA ROCHELLE VILLE", "POITIERS", "TOURS", "ANGERS ST LAUD", "NANTES", "RENNES",
    "LE MANS", "BREST", "QUIMPER", "VANNES", "ST MALO", "DIJON VILLE", "BESANCON FRANCHE COMTE TGV",
    "GRENOBLE", "CHAMBERY CHALLES LES EAUX", "ANNECY", "NICE VILLE", "TOULON", "CANNES", "ST ETIENNE CHATEAUCREUX",
    "VALENCE TGV", "REIMS", "CHAMPAGNE ARDENNE TGV", "ROUEN RIVE DROITE", "LE HAVRE", "DUNKERQUE",
    "ARRAS", "CALAIS FRETHUN", "LORIENT", "ANGOULEME", "LIMOGES BENEDICTINS", "CLERMONT FERRAND",
]


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
