import os
from pathlib import Path

# Загружаем .env вручную если файл существует
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            key, _, value = line.partition('=')
            os.environ[key.strip()] = value.strip()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost/library_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'covers')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    BOOKS_PER_PAGE = 10
    REVIEWS_PER_PAGE = 10
