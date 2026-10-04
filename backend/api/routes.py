from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

from flask import Blueprint, current_app, jsonify, request

from domain.planner import Planner
from services import navitia_client, opendata_client

bp = Blueprint("api", __name__, url_prefix="/api")


class BadRequest(ValueError):
    pass


@bp.errorhandler(BadRequest)
def _bad_request(e):
    return jsonify(error=str(e)), 400


@bp.errorhandler(opendata_client.OpenDataError)
def _upstream(e):
    return jsonify(error=str(e), retryable=True), 502


def _parse_date(value, name: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise BadRequest(f"'{name}' doit être au format AAAA-MM-JJ")


def _csv(value) -> list[str]:
    if isinstance(value, list):
        return [v.strip() for v in value if v and v.strip()]
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def _planner(date_from: date, date_to: date) -> Planner:
    cfg = current_app.config
    lo, hi = date_from - timedelta(days=1), date_to  # D-1 needed for overnight
    trains = opendata_client.fetch_trains(cfg["OPENDATA_URL"], lo, hi, cfg["CACHE_TTL"])
    return Planner(trains, now=datetime.now())


MAX_ROUTES = 40


def _route_id(origin: str, destination: str) -> str:
    return f"{origin} → {destination}"


def _routes(origins: list[str], destinations: list[str]) -> list[tuple[str, str]]:
    if not origins or not destinations:
        raise BadRequest("Au moins une origine et une destination sont requises")
    routes = [(o, d) for o in origins for d in destinations if o.strip().lower() != d.strip().lower()]
    if not routes:
        raise BadRequest("L'origine et la destination doivent être différentes")
    if len(routes) > MAX_ROUTES:
        raise BadRequest(f"Trop de trajets ({len(routes)}), maximum {MAX_ROUTES}")
    return routes


def _legs(value) -> int:
    try:
        return max(1, min(4, int(value or 3)))
    except (TypeError, ValueError):
        raise BadRequest("'max_legs' invalide")


def _days(a: date, b: date):
    for i in range((b - a).days + 1):
        yield a + timedelta(days=i)


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/stations")
def stations():
    cfg = current_app.config
    names = navitia_client.search_stations(
        request.args.get("q", ""), cfg["NAVITIA_TOKEN"], cfg["NAVITIA_BASE_URL"]
    )
    return jsonify(stations=names)


@bp.post("/search")
def search():
    body = request.get_json(silent=True) or {}
    routes = _routes(_csv(body.get("origins")), _csv(body.get("destinations")))
    d_from, d_to = _parse_date(body.get("date_from"), "date_from"), _parse_date(body.get("date_to"), "date_to")
    if d_to < d_from or (d_to - d_from).days + 1 > current_app.config["MAX_RANGE_DAYS"]:
        raise BadRequest(f"Plage de dates invalide (max {current_app.config['MAX_RANGE_DAYS']} jours)")
    hubs, legs, overnight = _csv(body.get("hubs")), _legs(body.get("max_legs")), bool(body.get("overnight"))

    planner = _planner(d_from, d_to)  # one fetch shared by all origins

    def run(route: tuple[str, str]) -> dict:
        out = {}
        for day in _days(d_from, d_to):
            summary = planner.summarize(planner.find(route[0], route[1], day, hubs, legs, overnight))
            if summary:
                out[day.isoformat()] = summary
        return out

    with ThreadPoolExecutor(max_workers=min(8, len(routes))) as pool:
        results = list(pool.map(run, routes))
    ids = [_route_id(o, d) for o, d in routes]
    return jsonify(days=dict(zip(ids, results)))


@bp.get("/day")
def day():
    a = request.args
    routes = _routes(_csv(a.get("origins")), _csv(a.get("destinations")))
    d = _parse_date(a.get("date"), "date")
    planner = _planner(d, d)
    hubs, legs, overnight = _csv(a.get("hubs")), _legs(a.get("max_legs")), a.get("overnight") in ("1", "true")
    return jsonify(
        date=d.isoformat(),
        itineraries={
            _route_id(o, dest): [i.to_dict() for i in planner.find(o, dest, d, hubs, legs, overnight)]
            for o, dest in routes
        },
    )
