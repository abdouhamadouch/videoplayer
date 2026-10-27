FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV ENABLE_BROWSER_FALLBACK=false
ENV TRANSCODE_HWACCEL=
ENV PORT=10000

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/antlis/tg-streaming-bot.git /opt/tg-streaming-bot
WORKDIR /opt/tg-streaming-bot
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY web_wrapper.py /opt/tg-streaming-bot/web_wrapper.py

CMD ["python3", "web_wrapper.py"]
