import os


class Config:
    NAVITIA_TOKEN = os.getenv("NAVITIA_TOKEN", "")
    NAVITIA_BASE_URL = os.getenv("NAVITIA_BASE_URL", "https://api.navitia.io/v1/coverage/sncf")
    OPENDATA_URL = os.getenv(
        "OPENDATA_URL",
        "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/exports/json",
    )
    CACHE_TTL = int(os.getenv("CACHE_TTL", "900"))
    MAX_RANGE_DAYS = 62
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4200")
