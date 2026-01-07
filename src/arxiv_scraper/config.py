# Arquivo: src/arxiv_scraper/config.py
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Definições de caminhos absolutos
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    """
    Configurações da aplicação. PydanticSettings gerencia a leitura de .env.
    """

    SCRAPE_URL: str = Field(
        default="https://arxiv.org/list/cs.CL/recent",
        description="URL alvo para o web scraping (Computation and Language).",
    )
    DATABASE_PATH: Path = Field(
        default=DATA_DIR / "arxiv_data.duckdb",
        description="Caminho do arquivo DuckDB para persistência.",
    )
    TABLE_NAME: str = Field(
        default="arxiv_articles", description="Nome da tabela no banco de dados."
    )
    CSV_PATH: Path = Field(
        default=DATA_DIR / "arxiv_data.csv",
        description="Caminho do arquivo CSV para persistência.",
    )
    REQUEST_DELAY: float = Field(
        default=0.2, description="Tempo entre requests para evitar sobrecarga."
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Instância única das configurações (Design Pattern: Singleton implícito)
settings = Settings()

# Garante que o diretório de dados existe
DATA_DIR.mkdir(exist_ok=True)
