# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     GROQ_API_KEY: str
#     GEMINI_API_KEY: str
#     MONGODB_URL: str = "mongodb://localhost:27017"
#     DB_NAME: str = "agentsec"
#     CHROMA_PERSIST_DIR: str = "./chroma_db"
#     SECRET_KEY: str = "change-this-in-production"

#     class Config:
#         env_file = ".env"

# settings = Settings()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GEMINI_API_KEY: str
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "agentsec"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    SECRET_KEY: str = "change-this-in-production"
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()