# ULTIMATE MAX Planner

Calendrier interactif des trajets TGV MAX / MAX JEUNE à 0 €, avec correspondances, nuitée la veille et recherche multi-origines (une couleur par origine).

- `backend/` — Flask : agrégation des disponibilités + algorithme de correspondances/nuitée
- `frontend/` — Angular 20 + RxJS + FullCalendar

**Données** : la disponibilité MAX vient du dataset SNCF Open Data `tgvmax` (`od_happy_card = OUI`, sans clé). Navitia ne donne pas cette disponibilité ; un token Navitia (optionnel) sert uniquement à l'autocomplétion des gares. Le dataset ne couvre qu'environ 30 jours à venir et ne contient que des trains directs : les correspondances sont calculées par chaînage.

**Aucune donnée fictive** : seuls des trains réels du dataset sont proposés (trains déjà partis exclus, doublons supprimés). Si l'API SNCF est indisponible, une erreur s'affiche avec un bouton « Réessayer ».

**Mémoire** : les recherches récentes (10 max) et les favoris ⭐ sont conservés dans le navigateur (localStorage) ; un clic relance le trajet à partir d'aujourd'hui sur la même durée.

## Prérequis
Python ≥ 3.11, Node ≥ 20.19 / 22.12.

## Backend (http://localhost:5000)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                      # tests de l'algorithme
python app.py
```
Variables : `NAVITIA_TOKEN` (optionnel), `CACHE_TTL` (s, défaut 900), `CORS_ORIGINS`.

## Frontend (http://localhost:4200)
```bash
cd frontend
npm install
npm start                   # ng serve, /api proxifié vers :5000
```

## API
- `GET /api/stations?q=` — autocomplétion
- `POST /api/search` `{origins[], destinations[], date_from, date_to, hubs[], overnight, max_legs}` → résumé par origine et par jour
- `GET /api/day?origins=A,B&destinations=C,D&date=&hubs=&overnight=&max_legs=` → itinéraires détaillés

## Algorithme (`backend/domain/planner.py`)
- Escales autorisées : Paris (toutes gares), Massy, Marne-la-Vallée Chessy, CDG 2 + villes ajoutées par l'utilisateur (`hubs`).
- Correspondance ≥ 30 min (≥ 75 min à Paris : le dataset ne distingue pas les gares parisiennes), amplitude ≤ 18 h, 1 à 4 trains.
- Nuitée : tronçon(s) la veille après 17 h jusqu'à une ville-escale, ≥ 4 h de repos, puis suite le lendemain dès 5 h. Le jour affiché au calendrier est celui de l'arrivée.
