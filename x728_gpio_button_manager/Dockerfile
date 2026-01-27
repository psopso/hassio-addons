FROM ghcr.io/home-assistant/aarch64-base:latest

USER root

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    libgpiod \
    build-base \
    python3-dev \

# Install python library
RUN pip install --no-cache-dir gpiod requests --break-system-packages

# Copy our files
COPY x728_manager_gpio.py /x728_manager_gpio.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh

COPY README.md /README.md

# Run it
# CMD ["python3", "-u", "/x728_manager_gpio.py"]

CMD ["/run.sh"]
