from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = "dev-key-change-in-prod"
    DATA_DIR = BASE_DIR / "data" 
    DEBUG = False


class DevConfig(Config):
    DEBUG = True
