from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base de datos
    database_url: str

    # Tiempo límite de votación (pendiente de definir, configurable vía .env)
    tiempo_limite_voto_minutos: int = 5

    # Entorno de ejecución
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


# Instancia única compartida en toda la aplicación
# Uso: from app.config import settings; settings.database_url
settings = Settings()
