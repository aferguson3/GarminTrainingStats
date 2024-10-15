from backend.server import create_app
from backend.server.config import db, cache, BaseConfig

APP_CONFIG = BaseConfig()

app = create_app(db, cache, app_config=APP_CONFIG)


def main():
    create_app(db, cache, app_config=APP_CONFIG)


if __name__ == "__main__":
    main()
