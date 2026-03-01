from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Face Attendance System"
    app_version: str = "2.0.0"
    database_url: str = f"sqlite:///{BASE_DIR}/data/attendance.db"
    faces_dir: Path = BASE_DIR / "data" / "faces"
    models_dir: Path = BASE_DIR / "data" / "models"
    encodings_file: Path = BASE_DIR / "data" / "models" / "encodings.pkl"
    tolerance: float = 0.5
    frame_scale: float = 0.5
    camera_index: int = 0
    debug: bool = False
    secret_key: str = "change-this-in-production"

    class Config:
        env_file = ".env"


settings = Settings()
