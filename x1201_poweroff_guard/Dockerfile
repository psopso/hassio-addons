FROM ghcr.io/home-assistant/aarch64-base:latest

USER root

RUN apk add --no-cache \
    python3 \
    py3-pip \
    libgpiod

RUN pip install --no-cache-dir gpiod --break-system-packages

COPY x1201_guard.py /x1201_guard.py

#CMD [ "python3", "/x1201_guard.py" ]

COPY rootfs /

RUN chmod a+x /etc/services.d/x1201_guard/run /etc/services.d/x1201_guard/finish
