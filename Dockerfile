FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Jakarta

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from mcp.server.fastmcp import FastMCP; print('FastMCP import OK')"

COPY config ./config
COPY models ./models
COPY services ./services
COPY scripts ./scripts
COPY tools ./tools
COPY server.py ./

EXPOSE 3000

CMD ["python", "server.py"]
