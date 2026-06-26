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

# Aplica migrações e sobe o servidor de produção (gunicorn)
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
