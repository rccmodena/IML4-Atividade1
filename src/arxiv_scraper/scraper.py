# Arquivo: src/arxiv_scraper/scraper.py
import requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin

# Importações internas
from .models import Article
from .config import settings
from .database import DuckDBManager


def parse_arxiv_article(dt_tag: BeautifulSoup, dd_tag: BeautifulSoup) -> Article:
    """
    Extrai os dados de um par <dt> (ID) e <dd> (Detalhes) da lista do Arxiv 
    e retorna um objeto Article validado pelo Pydantic.
    """
    
    # 1. Extração do ID e Link
    # O ID completo está no texto do link 'Abstract'
    arxiv_id_full = dt_tag.find('a', title='Abstract').text.strip()
    arxiv_id = arxiv_id_full.split(':')[-1] # Ex: "2312.06733"
    
    # Constrói o link absoluto
    relative_link = dt_tag.find('a', title='Abstract')['href']
    absolute_link = urljoin("https://arxiv.org/", relative_link)

    # 2. Extração do Título
    # O título está dentro de uma div com classe 'list-title'
    title = dd_tag.find('div', class_='list-title').text.replace('Title: ', '').strip()

    # 3. Extração dos Autores
    # Os autores são links <a> dentro da div 'list-authors'
    author_tags = dd_tag.find('div', class_='list-authors').find_all('a')
    authors = [tag.text.strip() for tag in author_tags]
    
    # 4. Extração de Sujeitos e Data de Submissão
    # O Arxiv agrupa sujeitos e a data de submissão na mesma linha.
    subjects_line = dd_tag.find('div', class_='list-subjects').text.replace('Subjects: ', '').strip()
    
    # A data de submissão está no final da linha e é separada por '[Submitted ...]'
    submission_date = subjects_line.split(' [Submitted ')[-1].replace(']', '')
    subjects = subjects_line.split(' [Submitted ')[0].strip()

    # Observação: O resumo (summary) completo não está na página de lista.
    # Usamos um placeholder para manter o modelo Pydantic completo.
    summary = "Summary not available in list view."

    # Retorna o objeto validado (Pydantic garantirá que os tipos estão corretos)
    return Article(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors,
        subjects=subjects,
        summary=summary,
        link=absolute_link,
        submission_date=submission_date
    )


def scrape_arxiv(url: str) -> List[Article]:
    """Realiza o scraping da página do Arxiv e retorna uma lista de objetos Article validados."""
    print(f"🌐 Iniciando scraping da URL: {url}")
    
    try:
        # 1. Requisição: Timeout definido para boas práticas
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Lança HTTPError para respostas ruins (4xx, 5xx)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar a URL: {e}")
        return []

    # 2. Parsing: Usa o 'html.parser' que é nativo e rápido
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # O Arxiv usa listas de definição: <dl> para a lista de artigos
    dl_list = soup.find('dl')
    
    if not dl_list:
        print("Nenhuma lista de artigos (<dl>) encontrada. O scraping falhou.")
        return []

    # Os detalhes de cada artigo estão em tags <dt> (ID) e <dd> (Detalhes)
    dt_tags = dl_list.find_all('dt')
    dd_tags = dl_list.find_all('dd')
    
    if len(dt_tags) != len(dd_tags):
        print("Aviso: Número de tags <dt> e <dd> não corresponde. Os dados podem estar incompletos.")

    articles: List[Article] = []
    
    # 3. Extração e Validação em Loop
    for dt, dd in zip(dt_tags, dd_tags):
        try:
            # Chama a função de parsing e validação Pydantic
            article = parse_arxiv_article(dt, dd)
            articles.append(article)
        except Exception as e:
            # Tratamento de erro específico para uma linha, permitindo que o loop continue
            print(f"⚠️ Erro ao parsear um artigo: {e}")
            continue

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
    
    print("✨ Processo de extração e persistência concluído com sucesso.")


if __name__ == "__main__":
    # Ponto de entrada da aplicação
    main()