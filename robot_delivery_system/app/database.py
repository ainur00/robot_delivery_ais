from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Создаем движок для подключения к БД
engine = create_engine(
    settings.DATABASE_URL,
    echo = True,
    pool_pre_ping = True,
    pool_recycle = 3600,
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    """
    Генератор сессии БД для использования в FastAPI зависимостях
    Использование:
        db = next(get_db())
        или в FastAPI: Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания всех таблиц
def create_tables():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы успешно")

# Функция для удаления всех таблиц (для тестов)
def drop_tables():
    """Удаляет все таблицы из БД"""
    Base.metadata.drop_all(bind=engine)
    print("Таблицы удалены")
