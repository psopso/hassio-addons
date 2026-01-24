FROM ghcr.io/home-assistant/aarch64-base:latest

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    libgpiod \
    libgpiod-dev \
    build-base \
    python3-dev

# Install python library
RUN pip install gpiod --break-system-packages

# Copy our files
COPY x728_manager_gpio.py /x728_manager_gpio.py
COPY README.md /README.md

# Run it
CMD ["python3", "-u", "/x728_manager_gpio.py"]