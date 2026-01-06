# ArXiv Scraper - Computation and Language (cs.CL)

Este projeto consiste em um mecanismo de extração de dados (**Web Scraper**) desenvolvido para coletar informações sobre artigos científicos recentes da seção *Computation and Language* do portal **ArXiv**. O sistema extrai metadados, garante a persistência em um banco de dados analítico e utiliza esteiras de **CI/CD** para automação.



---

## 🚀 Funcionalidades

* **Extração Automatizada:** Coleta de títulos, autores, datas de submissão e links diretamente da URL: `https://arxiv.org/list/cs.CL/recent`.
* **Persistência em DuckDB:** Armazenamento dos dados em um banco de dados colunar de alta performance, ideal para análise de dados.
* **Containerização:** Aplicação totalmente empacotada em Docker para garantir a reprodutibilidade.
* **Automação CI/CD:** Pipeline configurado no GitHub Actions para build e push automático da imagem para o Docker Hub.

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Finalidade |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.11 | Lógica de scraping e processamento |
| **Ambiente** | Poetry | Gerenciamento de dependências e ambiente virtual |
| **Web Scraping** | BeautifulSoup4 / Requests | Parsing de HTML e requisições HTTP |
| **Banco de Dados** | DuckDB | Persistência de dados local em formato OLAP |
| **Container** | Docker | Portabilidade e isolamento |
| **CI/CD** | GitHub Actions | Esteira automatizada de build e deploy |

---

## 📂 Estrutura de Dados (DuckDB)

Os dados são armazenados na tabela `arxiv_articles` dentro do banco `data/arxiv_data.duckdb`.

* `title`: Título completo do artigo.
* `authors`: Nomes dos autores.
* `submission_date`: Data de submissão no ArXiv.
* `link`: URL de acesso ao resumo/PDF.

---

## ⚙️ Como Executar

### 1. Execução Local (via Poetry)
Certifique-se de ter o Python 3.11 e o Poetry instalados.

```bash
# Instalar as dependências do projeto
poetry install

# Executar o scraper
poetry run python -m arxiv_scraper.scraper