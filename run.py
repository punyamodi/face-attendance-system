import uvicorn
from app.main import app
from app.database.connection import create_tables
from app.config import settings


def main():
    create_tables()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
