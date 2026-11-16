# Terra Twin backend — Vercel container service.
# Scientific stack (rasterio/GDAL-linked wheels) needs libexpat.so.1, which the
# default Vercel python3.12 runtime does not ship. A container service gives us
# full system-library control and preserves the exact scientific rasterio stack.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONPATH=/app
EXPOSE 80
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
