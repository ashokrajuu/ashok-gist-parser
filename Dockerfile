# Stage 1: build
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

# Non-root user
RUN useradd -m apiuser
USER apiuser

EXPOSE 8080
HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "gistCheck.py"]
