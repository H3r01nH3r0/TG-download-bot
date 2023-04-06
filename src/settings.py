from pydantic import BaseSettings


class Settings(BaseSettings):
    bot_token: str = "5642416515:AAE8iXT8el6KukDAI2F4ciaqUAFb33_7Vpw"
    database_url: str = "sqlite:///./database.sqlite3"


settings = Settings()
