# Arquivo: src/arxiv_scraper/models.py
import csv
from pathlib import Path
from typing import List

from pydantic import BaseModel, HttpUrl

from .config import settings


class Article(BaseModel):
    """
    Define o esquema de dados para um artigo extraído do Arxiv.
    Usamos Pydantic para garantir a tipagem e validação dos dados.
    """

    arxiv_id: str
    title: str
    authors: str
    subjects: str
    abstract: str
    link: HttpUrl  # Pydantic valida se é uma URL válida
    submission_date: str

    class Config:
        """Configurações adicionais para o Pydantic."""

        from_attributes = True


def save_articles_to_csv(data: List[Article], filename: Path = settings.CSV_PATH):
    """
    Salvar os artigos em arquivo CSV.
    """

    fieldnames = list(Article.model_fields.keys())  # For Pydantic V2

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row_model in data:
            writer.writerow(row_model.model_dump())
