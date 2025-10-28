from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    SENTENCE_TRANSFORMER_MODEL: str
    
    DEFAULT_TOP_N: int
    DEFAULT_THRESHOLD: float
    DEFAULT_AMOUNT_WEIGHT: float
    DEFAULT_DATE_WEIGHT: float
    DEFAULT_CONTACT_WEIGHT: float
    DEFAULT_DATE_METHOD: str
    
    API_HOST: str
    API_PORT: int
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
