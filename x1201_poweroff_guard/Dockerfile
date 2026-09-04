FROM ghcr.io/home-assistant/aarch64-base:latest

USER root

RUN apk add --no-cache \
    python3 \
    py3-pip \
    libgpiod

RUN pip install --no-cache-dir gpiod --break-system-packages

COPY x1201_guard.py /x1201_guard.py
COPY run.sh /run.sh

RUN chmod +x /run.sh

CMD ["/run.sh"]
