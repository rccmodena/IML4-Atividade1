# ArXiv Scraper - Computation and Language (cs.CL)

Nome: Rudi César Comiotto Modena.

Trabalho realizado em conjunto com:
- Márcio Leandro
- Mônica Mendes

Este projeto consiste em um mecanismo de extração de dados (**Web Scraper**) desenvolvido para coletar informações sobre artigos científicos recentes da seção _Computation and Language_ do portal **ArXiv**. O sistema extrai metadados, garante a persistência em um banco de dados analítico, arquivo CSV e utiliza esteiras de **CI/CD** para automação.

---

## 🚀 Funcionalidades

- **Extração Automatizada:** Coleta de títulos, autores, datas de submissão e links diretamente da URL: `https://arxiv.org/list/cs.CL/recent`.
- **Persistência em DuckDB:** Armazenamento dos dados em um banco de dados colunar de alta performance, ideal para análise de dados.
- **Persistência em CSV:** Armazenamento dos dados em um arquivo CSV, formato muito utilizado em análise de dados.
- **Containerização:** Aplicação totalmente empacotada em Docker para garantir a reprodutibilidade.
- **Automação CI/CD:** Pipeline configurado no GitHub Actions para build e push automático da imagem para o Docker Hub.

---

## 🛠️ Stack Tecnológica

| Camada             | Tecnologia                | Finalidade                                       |
| :----------------- | :------------------------ | :----------------------------------------------- |
| **Linguagem**      | Python 3.11               | Lógica de scraping e processamento               |
| **Ambiente**       | Poetry                    | Gerenciamento de dependências e ambiente virtual |
| **Web Scraping**   | BeautifulSoup4 / Requests | Parsing de HTML e requisições HTTP               |
| **Banco de Dados** | DuckDB                    | Persistência de dados local em formato OLAP      |
| **Exportar Dados** | CSV                       | Persistência de dados local em formato texto     |
| **Container**      | Docker                    | Portabilidade e isolamento                       |
| **CI/CD**          | GitHub Actions            | Esteira automatizada de build e deploy           |

---

## 📂 Estrutura de Dados (DuckDB e CSV)

Os dados são armazenados na tabela `arxiv_articles` dentro do banco `data/arxiv_data.duckdb`, e também no arquivo `data/arxiv_data.csv`.

- `arxiv_id`: ID do artigo.
- `title`: Título completo do artigo.
- `authors`: Texto com os nomes dos autores separados por vírgula.
- `subjects`: Texto com os assuntos do artigo separados por vírgula..
- `abstract`: Resumo do Artigo.
- `link`: URL de acesso ao resumo/PDF.
- `submission_date`: Data de submissão no ArXiv.

---

## ⚙️ Como Executar

### 1. Execução Local (via Poetry)

Certifique-se de ter o Python 3.11 e o Poetry instalados.

```bash
# Instalar as dependências do projeto
poetry install

# Executar o scraper
poetry run python -m arxiv_scraper.scraper
```
