FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV ENABLE_BROWSER_FALLBACK=false
ENV TRANSCODE_HWACCEL=
ENV PORT=10000

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Pin upstream to a known revision: do not silently pull incompatible code on every build.
RUN git clone https://github.com/antlis/tg-streaming-bot.git /opt/tg-streaming-bot \
    && git -C /opt/tg-streaming-bot checkout a2ef52ec6247411ddbb44bc117dec67ff21f4b96

WORKDIR /opt/tg-streaming-bot
RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    && mkdir -p /opt/tg-streaming-bot/downloads \
    && chmod 755 /opt/tg-streaming-bot/downloads

COPY main.py /opt/tg-streaming-bot/main.py
COPY web_wrapper.py /opt/tg-streaming-bot/web_wrapper.py

CMD ["python3", "web_wrapper.py"]
