FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/backend
WORKDIR /app
COPY backend/requirements.lock /app/backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY backend /app/backend
COPY research /app/research
RUN useradd --uid 10001 --create-home academy && mkdir /app/data && chown academy:academy /app/data
USER academy
EXPOSE 8000
CMD ["uvicorn", "academy.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
