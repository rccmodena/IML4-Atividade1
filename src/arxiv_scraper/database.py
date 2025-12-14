# Arquivo: src/arxiv_scraper/database.py
import duckdb
from typing import List
from pathlib import Path
# Importamos as classes do nosso próprio pacote
from .models import Article
from .config import settings

class DuckDBManager:
    """
    Design Pattern: Gerenciador de Recurso.
    Gerencia a conexão e operações com o banco de dados DuckDB.
    """

    def __init__(self, db_path: Path = settings.DATABASE_PATH):
        """Inicializa o gerenciador e a conexão."""
        self.db_path = db_path
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        """Cria a conexão e a tabela se não existir."""
        self.conn = duckdb.connect(database=str(self.db_path), read_only=False)
        self.conn.sql(f"""
            -- Cria a tabela com arxiv_id como Chave Primária para evitar duplicatas
            CREATE TABLE IF NOT EXISTS {settings.TABLE_NAME} (
                arxiv_id VARCHAR PRIMARY KEY,
                title VARCHAR,
                authors VARCHAR,
                subjects VARCHAR,
                summary VARCHAR,
                link VARCHAR,
                submission_date VARCHAR
            );
        """)

    def insert_articles(self, articles: List[Article]):
        """Insere uma lista de artigos no banco de dados, ignorando duplicatas existentes."""
        if not articles:
            print("Nenhum artigo para inserir.")
            return

        # Prepara os dados: Pydantic Article -> Lista de Tuplas
        data_to_insert = [
            (
                article.arxiv_id,
                article.title,
                # Armazena a lista de autores como uma string separada por vírgula
                ", ".join(article.authors),
                article.subjects,
                article.summary,
                str(article.link),
                article.submission_date,
            )
            for article in articles
        ]

        try:
            placeholders = ", ".join(["?"] * 7)
            query = f"""
                -- Tenta inserir, se o arxiv_id já existir (conflito PK), ignora a linha
                INSERT INTO {settings.TABLE_NAME} VALUES ({placeholders})
                ON CONFLICT (arxiv_id) DO NOTHING;
            """
            
            # Execução em massa para melhor performance
            self.conn.executemany(query, data_to_insert)
            self.conn.commit()
            print(f"✅ Inseridos/atualizados {self.conn.row_count} novos artigos.")
        except Exception as e:
            print(f"❌ Erro ao inserir dados: {e}")
            self.conn.rollback()

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            print("Conexão DuckDB fechada.")