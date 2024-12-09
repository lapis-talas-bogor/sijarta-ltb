FROM python:3.11.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py apply_sql_migrations && gunicorn sijarta_ltb.wsgi:application --bind 0.0.0.0:8000"]

