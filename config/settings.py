from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    bot_token: str = ""
    spoonacular_api_key: str = ""
    admin_ids: str = "872063132, 7445452111"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()