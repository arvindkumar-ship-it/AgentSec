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
from pydantic import model_validator

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "agentsec"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    SECRET_KEY: str = "change-this-in-production"
    SENTRY_DSN: str = ""
    ENVIRONMENT: str = "development"
    PLATFORM_ADMIN_EMAILS: str = ""

    @model_validator(mode="after")
    def production_secret(self):
        if self.ENVIRONMENT.lower() == "production" and (len(self.SECRET_KEY) < 32 or self.SECRET_KEY == "change-this-in-production"):
            raise ValueError("Set a random SECRET_KEY of at least 32 characters in production")
        return self

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
