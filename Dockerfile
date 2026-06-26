# Imagem base enxuta com Python
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

EXPOSE 8000

# Aplica migrações, coleta os estáticos (admin/Swagger) e sobe o gunicorn.
# Tudo roda no START do container, quando as variáveis de ambiente
# (SECRET_KEY etc.) já estão disponíveis — por isso o collectstatic NÃO
# fica em um RUN durante o build (onde não há SECRET_KEY e quebraria).
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
