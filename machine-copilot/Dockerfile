# Edge-deployable image — designed to run on the machine controller's
# onboard PC or an adjacent gateway box, not a data-center server.
FROM python:3.12-slim

WORKDIR /srv/machine-copilot

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY app/ app/
COPY DATA/ DATA/
COPY processed_data/ processed_data/

ENV MACHINE_MODEL=Apex-3200
ENV OFFLINE_MODE=false

EXPOSE 8000

# Run ingestion at build/first-boot if processed_data is empty, then serve.
CMD ["sh", "-c", "test -f processed_data/*.pkl || python -m app.ingestion.processor; uvicorn app.main:app --host 0.0.0.0 --port 8000"]
