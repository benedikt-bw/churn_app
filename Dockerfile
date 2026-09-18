FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN python -m pip install --no-cache-dir uv==0.12.16 \
    && uv sync --locked --no-dev

COPY app.py dashboard.py ./

EXPOSE 8501

CMD ["uv", "run", "--no-dev", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
