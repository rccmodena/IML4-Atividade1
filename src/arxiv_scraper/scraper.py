import datetime
import time
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .config import settings
from .database import DuckDBManager

# Importações internas
from .models import Article, save_articles_to_csv


def parse_arxiv_article(dt_tag: BeautifulSoup, dd_tag: BeautifulSoup) -> Article:
    """
    Extrai os dados de um par <dt> (ID) e <dd> (Detalhes) da lista do Arxiv
    e retorna um objeto Article validado pelo Pydantic.
    """

    # 1. Extração do ID e Link
    # O ID completo está no texto do link 'Abstract'
    arxiv_id_full = dt_tag.find("a", title="Abstract").text.strip()
    arxiv_id = arxiv_id_full.split(":")[-1]  # Ex: "2312.06733"

    print(f"🌐 Extraindo detalhes dos artigo: {arxiv_id}")

    # Constrói o link absoluto
    relative_link = dt_tag.find("a", title="Abstract")["href"]
    absolute_link = urljoin("https://arxiv.org/", relative_link)

    # 2. Extração do Título
    # O título está dentro de uma div com classe 'list-title'
    title_div = dd_tag.find("div", class_="list-title")

    # Remove a descrição "Title"
    descriptor = title_div.find("span", class_="descriptor")
    if descriptor:
        descriptor.decompose()

    title = title_div.get_text(" ", strip=True)

    # 3. Extração dos Autores
    # Os autores são links <a> dentro da div 'list-authors'
    author_tags = dd_tag.find("div", class_="list-authors").find_all("a")
    authors = [tag.text.strip() for tag in author_tags]
    authors = ", ".join(authors)

    # 4. Extração de Assuntos
    # O Arxiv agrupa assuntos
    subjects_div = dd_tag.find("div", class_="list-subjects")

    # Remove a descrição "Subjects"
    descriptor = subjects_div.find("span", class_="descriptor")
    if descriptor:
        descriptor.decompose()

    subjects = [
        sub.strip() for sub in subjects_div.get_text(" ", strip=True).split(";")
    ]
    subjects_str = ", ".join(subjects)

    # 5. Data de submissão e Resumo
    # Para adquirir essas informações é necessário fazer um novo request.
    try:
        # 1. Requisição: Timeout definido para boas práticas
        response = requests.get(absolute_link, timeout=15)
        response.raise_for_status()  # Lança HTTPError para respostas ruins (4xx, 5xx)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar a URL: {e}")
        return []

    # 2. Parsing: Usa o 'html.parser' que é nativo e rápido
    detailed_soup = BeautifulSoup(response.content, "html.parser")

    test_div = (
        detailed_soup.find("div", class_="dateline")
        .get_text(" ", strip=True)
        .replace("Submitted on ", "")
        .strip()
    )

    date_string = test_div[1:-1]
    submission_date = datetime.datetime.strptime(date_string, "%d %b %Y").strftime(
        "%Y-%m-%d"
    )

    abstract_blockquote = detailed_soup.find("blockquote", class_="abstract")

    # Remove a descrição "Abstract"
    descriptor = abstract_blockquote.find("span", class_="descriptor")
    if descriptor:
        descriptor.decompose()

    abstract = abstract_blockquote.get_text(" ", strip=True)

    # Retorna o objeto validado (Pydantic garantirá que os tipos estão corretos)
    return Article(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        subjects=subjects_str,
        abstract=abstract,
        link=absolute_link,
        submission_date=submission_date,
    )


def scrape_arxiv(url: str) -> List[Article]:
    """
    Realiza o scraping da página do Arxiv e retorna
    uma lista de objetos Article validados.
    """
    print(f"🌐 Iniciando scraping da URL: {url}")

    try:
        # 1. Requisição: Timeout definido para boas práticas
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # Lança HTTPError para respostas ruins (4xx, 5xx)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar a URL: {e}")
        return []

    # 2. Parsing: Usa o 'html.parser' que é nativo e rápido
    soup = BeautifulSoup(response.content, "html.parser")

    # O Arxiv usa listas de definição: <dl> para a lista de artigos
    dl_list = soup.find("dl")

    if not dl_list:
        print("Nenhuma lista de artigos (<dl>) encontrada. O scraping falhou.")
        return []

    # Os detalhes de cada artigo estão em tags <dt> (ID) e <dd> (Detalhes)
    dt_tags = dl_list.find_all("dt")
    dd_tags = dl_list.find_all("dd")

    if len(dt_tags) != len(dd_tags):
        print(
            "Aviso: Número de tags <dt> e <dd> não corresponde. "
            "Os dados podem estar incompletos."
        )

    articles: List[Article] = []

    # 3. Extração e Validação em Loop
    for dt, dd in zip(dt_tags, dd_tags, strict=True):  # Corrigido B905
        try:
            # Chama a função de parsing e validação Pydantic
            article = parse_arxiv_article(dt, dd)
            articles.append(article)
            # break
        except Exception as e:
            # Tratamento de erro específico para uma linha,
            # permitindo que o loop continue
            print(f"⚠️ Erro ao parsear um artigo: {e}")
            continue
        time.sleep(settings.REQUEST_DELAY)

    print(f"✅ Scraping concluído. {len(articles)} artigos extraídos.")
    return articles


def main():
    """Função principal que orquestra o scraping e a persistência."""

    # 1. Captura de Dados
    articles = scrape_arxiv(settings.SCRAPE_URL)

    if not articles:
        print("Não foi possível extrair artigos. Encerrando o processo.")
        return

    # 2. Armazenamento das Informações
    db_manager = DuckDBManager()

    # Design Pattern: Gerenciador de Recurso (DuckDBManager)
    db_manager.insert_articles(articles)
    db_manager.close()

    # Salvar os artigos em um arquivo CSV
    save_articles_to_csv(data=articles)

    print("✨ Processo de extração e persistência concluído com sucesso.")


if __name__ == "__main__":
    # Ponto de entrada da aplicação
    main()
