FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY automation ./automation
COPY config ./config
COPY k8s ./k8s
RUN useradd --create-home runner
USER runner
ENTRYPOINT ["python", "-m", "automation"]
CMD ["health"]
