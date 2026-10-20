# syntax=docker/dockerfile:1
# All Python services from one file, one target each (build context: repository root):
#
#   docker build -f services/Dockerfile --target chat .
#
# The API services share a slim base without PyTorch; only `inference` carries
# the models and PyTorch (CUDA wheels — runs on CPU too, the reranker slowly).
#
# Layer order: packages first, code last — a code change rebuilds only the small
# COPY layers, never the package installs (PyTorch alone is several GB).

FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY services/requirements.txt services/requirements.txt
COPY services/requirements-retrieval.txt services/requirements-retrieval.txt
RUN pip install -r services/requirements.txt -r services/requirements-retrieval.txt
RUN useradd --create-home --uid 10001 app
ENV PYTHONPATH=/app/services/common:/app/retrieval
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/health', timeout=3)"

# The code every service shares: service_common and the retrieval package.
FROM base AS shared
COPY services/common services/common
COPY retrieval/abb_retrieval retrieval/abb_retrieval

# --------------------------------------------------------------------------- #
FROM shared AS chat
COPY services/chat services/chat
ENV PYTHONPATH=$PYTHONPATH:/app/services/chat PORT=8001
USER app
EXPOSE 8001
CMD ["sh", "-c", "uvicorn chat_service.main:app --host 0.0.0.0 --port $PORT"]

# --------------------------------------------------------------------------- #
FROM shared AS analytics
COPY services/analytics services/analytics
ENV PYTHONPATH=$PYTHONPATH:/app/services/analytics PORT=8002
USER app
EXPOSE 8002
CMD ["sh", "-c", "uvicorn analytics_service.main:app --host 0.0.0.0 --port $PORT"]

# --------------------------------------------------------------------------- #
FROM base AS ingestion
# The chunker counts tokens with bge-m3's tokenizer (no PyTorch needed for that).
RUN pip install "transformers==5.20.0"
RUN mkdir -p /models && chown app /models
COPY services/common services/common
COPY retrieval/abb_retrieval retrieval/abb_retrieval
COPY services/ingestion services/ingestion
ENV PYTHONPATH=$PYTHONPATH:/app/services/ingestion PORT=8003 HF_HOME=/models
USER app
EXPOSE 8003
CMD ["sh", "-c", "uvicorn ingestion_service.main:app --host 0.0.0.0 --port $PORT"]

# --------------------------------------------------------------------------- #
FROM base AS scraper
COPY scraper/requirements.txt scraper/requirements.txt
RUN pip install -r scraper/requirements.txt
RUN mkdir -p /data && chown app /data
COPY services/common services/common
COPY retrieval/abb_retrieval retrieval/abb_retrieval
COPY scraper/abb_scraper scraper/abb_scraper
COPY services/scraper services/scraper
ENV PYTHONPATH=$PYTHONPATH:/app/scraper:/app/services/scraper PORT=8005 SCRAPER_DATA_DIR=/data
USER app
EXPOSE 8005
CMD ["sh", "-c", "uvicorn scraper_service.main:app --host 0.0.0.0 --port $PORT"]

# --------------------------------------------------------------------------- #
FROM base AS inference
# CUDA wheels by default; docker-compose.cpu.yml passes the CPU index (a much smaller image).
ARG TORCH_INDEX=https://download.pytorch.org/whl/cu128
RUN pip install torch==2.11.0 --index-url ${TORCH_INDEX} \
 && pip install "transformers==5.20.0" "FlagEmbedding==1.4.2"
RUN mkdir -p /models && chown app /models
COPY services/common services/common
COPY retrieval/abb_retrieval retrieval/abb_retrieval
COPY services/inference services/inference
ENV PYTHONPATH=$PYTHONPATH:/app/services/inference PORT=8004 HF_HOME=/models
USER app
EXPOSE 8004
# Loading both models takes a while on the first start (download into the /models volume).
HEALTHCHECK --interval=20s --timeout=5s --start-period=600s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8004/health', timeout=3)"
CMD ["sh", "-c", "uvicorn inference_service.main:app --host 0.0.0.0 --port $PORT"]
