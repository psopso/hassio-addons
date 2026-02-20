FROM ghcr.io/home-assistant/aarch64-base:latest

USER root

RUN apk add --no-cache \
    python3 \
    py3-pip \
    libgpiod

RUN pip install --no-cache-dir gpiod requests smbus2 paho-mqtt --break-system-packages

COPY x728_manager_gpio.py /x728_manager_gpio.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh

COPY README.md /README.md

CMD ["/run.sh"]
