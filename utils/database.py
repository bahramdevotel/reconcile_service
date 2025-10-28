from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import List

from models.database import Base, Invoice
from settings import settings


class DatabaseManager:
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self):
        self.engine = create_engine(
            settings.database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        print(f"Database connected: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)
        print("Database tables created/verified")
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def get_all_invoices(self) -> List[Invoice]:
        session = self.get_session()
        
        try:
            return session.query(Invoice).all()
        finally:
            session.close()


db_manager = DatabaseManager()
