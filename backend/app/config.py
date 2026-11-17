"""Configuración del backend: sale del entorno y, en local, del .env de la raíz del repositorio."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "venta_anticuario"
    mysql_user: str = "va_app"
    mysql_password: SecretStr | None = None

    # Cuánto dura la cookie de sesión en el navegador (entre 5 minutos y 30 días).
    session_ttl_minutes: int = Field(default=480, ge=5, le=43_200)

    # Usuarios que crea `init-db`: uno normal y un administrador. Sin contraseña no se crean.
    demo_user_username: str = ""
    demo_user_password: SecretStr | None = None
    admin_username: str = ""
    admin_password: SecretStr | None = None

    def database_url(self) -> URL:
        if self.mysql_password is None or not self.mysql_password.get_secret_value():
            raise RuntimeError("Falta MYSQL_PASSWORD: copia .env.example a .env y rellénalo.")
        # URL.create escapa la contraseña; montar la cadena a mano falla con símbolos como @ o /.
        return URL.create(
            "mysql+pymysql",
            username=self.mysql_user,
            password=self.mysql_password.get_secret_value(),
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
