# Minha Estante — Backend (API REST)

API REST do **Minha Estante**, um gerenciador de biblioteca pessoal de livros.
O usuário busca livros na API pública do **Google Books**, salva os que quiser
na sua estante, adiciona anotações e remove quando desejar (CRUD completo).

> Este repositório contém **apenas o backend**. O frontend (HTML/CSS/TypeScript)
> fica em um repositório separado.

## Integrantes do grupo

- Nome do Integrante 1 — matrícula
- Nome do Integrante 2 — matrícula

*(substitua pelos nomes reais antes da entrega)*

## Links

- **Site do backend (API):** `https://SUA-API.exemplo.com`
- **Documentação Swagger:** `https://SUA-API.exemplo.com/api/docs/`
- **Repositório do frontend:** `https://github.com/SEU-USUARIO/minha-estante-frontend`

## Tecnologias

- Python 3.12 + Django 5.1
- Django REST Framework (API REST)
- SimpleJWT (autenticação por tokens JWT)
- drf-spectacular (documentação OpenAPI / Swagger)
- django-cors-headers (liberação de CORS para o frontend)
- SQLite (desenvolvimento) / PostgreSQL (produção, opcional)

## Funcionalidades

- **CRUD completo** de livros na estante (`/api/livros/`).
- **Autenticação JWT**: login, refresh e cadastro com **ativação por e-mail**.
- **Endpoint protegido**: todas as rotas de livros exigem token válido.
- **Visões por usuário**: cada usuário só enxerga e manipula a própria estante.
- **Gerência de senha**: troca de senha e recuperação ("esqueci minha senha").
- **Busca de livros** via API do Google Books (`/api/search/`).
- **Swagger** com todos os endpoints documentados e testáveis.

## Principais endpoints

| Método | Rota | Descrição | Autenticado |
|---|---|---|---|
| POST | `/api/auth/register/` | Cadastra usuário (conta inativa) | Não |
| POST | `/api/auth/activate/` | Ativa a conta (uid + token) | Não |
| POST | `/api/auth/login/` | Retorna tokens JWT | Não |
| POST | `/api/auth/refresh/` | Renova o token de acesso | Não |
| POST | `/api/auth/password/change/` | Troca a senha | Sim |
| POST | `/api/auth/password/reset/` | Solicita recuperação de senha | Não |
| POST | `/api/auth/password/reset/confirm/` | Confirma nova senha | Não |
| GET/PATCH | `/api/profile/` | Lê e atualiza o perfil | Sim |
| GET | `/api/search/?q=` | Busca no Google Books | Sim |
| GET/POST | `/api/livros/` | Lista / adiciona livros | Sim |
| GET/PUT/PATCH/DELETE | `/api/livros/{id}/` | Detalhe / edita / remove | Sim |
| GET | `/api/docs/` | Swagger UI | Não |
| GET | `/api/schema/` | Schema OpenAPI | Não |

## Instalação local

Pré-requisitos: **Python 3.12+**.

```bash
# 1. Clone o repositório
git clone https://github.com/SEU-USUARIO/minha-estante-backend.git
cd minha-estante-backend

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env            # edite os valores conforme necessário

# 5. Aplique as migrações
python manage.py migrate

# 6. (opcional) crie um superusuário para acessar o /admin/
python manage.py createsuperuser

# 7. Rode o servidor
python manage.py runserver
```

A API ficará disponível em `http://localhost:8000` e o Swagger em
`http://localhost:8000/api/docs/`.

> **E-mails em desenvolvimento:** sem configuração SMTP, os e-mails de ativação
> e de recuperação de senha são **impressos no console** onde o servidor roda.
> Copie o link mostrado para ativar a conta / redefinir a senha.

## Variáveis de ambiente

Veja `.env.example`. As principais são:

- `SECRET_KEY` — chave secreta do Django.
- `DEBUG` — `True` em desenvolvimento, `False` em produção.
- `ALLOWED_HOSTS` — hosts permitidos (separados por vírgula).
- `CORS_ALLOWED_ORIGINS` — URLs do frontend liberadas para CORS.
- `FRONTEND_URL` — URL do frontend (usada nos links dos e-mails).
- `GBOOKS_API_KEY` — chave da API do Google Books (opcional).
- `DATABASE_URL` — string do PostgreSQL (opcional; sem ela, usa SQLite).
- `EMAIL_*` — configuração SMTP (opcional; sem ela, e-mails saem no console).

## Testes

```bash
python manage.py test
```

São 6 testes cobrindo proteção de endpoints, login com token, CRUD de livros
e isolamento entre usuários.

## Publicação

### Opção A — Docker

```bash
docker build -t minha-estante-backend .
docker run -p 8000:8000 --env-file .env minha-estante-backend
```

### Opção B — Provedor (Render / Railway / AWS)

O projeto inclui um `Procfile` e usa **WhiteNoise** para os arquivos estáticos.
Defina as variáveis de ambiente no painel do provedor e use o comando de start:

```bash
python manage.py migrate && gunicorn config.wsgi:application
```

## Imagens da aplicação

> Adicione aqui pelo menos três capturas de tela. Sugestões: Swagger UI,
> resposta de um endpoint protegido e a tela do `/admin/`.

![Swagger UI](docs/img/swagger.png)
![Listagem de livros](docs/img/livros.png)
![Painel admin](docs/img/admin.png)

## O que funcionou / o que não funcionou

**Funcionou (testado):**

- CRUD completo de livros pela API (testado via `curl` e testes automatizados).
- Cadastro com ativação por e-mail (link impresso no console em dev).
- Login/refresh JWT e bloqueio de endpoints sem token (401).
- Isolamento entre usuários (cada um vê só os próprios livros).
- Troca e recuperação de senha.
- Geração da documentação Swagger com todos os endpoints.

**Pontos de atenção:**

- A busca no Google Books depende de acesso externo à internet; em ambientes
  sem rede liberada, o endpoint retorna 503 (comportamento esperado e tratado).
- O envio real de e-mails exige configuração SMTP (`EMAIL_*`); em
  desenvolvimento, os e-mails são exibidos no console.
