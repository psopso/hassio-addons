ARG BUILD_FROM
FROM $BUILD_FROM
# RUN apk add --no-cache python3 py3-pip i2c-tools

# Instalace závislostí pro Python, I2C a grafiku
RUN apk add --no-cache \
    python3 \
    py3-pip \
    i2c-tools \
    freetype-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    zlib-dev \
    gcc \
    musl-dev \
    python3-dev

RUN python3 -m venv /venv
# RUN /venv/bin/pip install smbus2

# Instalace Pillow a luma.oled (toto chvíli potrvá, kompiluje se to)
RUN /venv/bin/pip install --break-system-packages smbus2 luma.oled Pillow
#RUN /venv/bin/pip install --break-system-packages smbus2 Adafruit-SSD1306 Pillow

# RUN pip3 install smbus2 --break-system-packages
COPY control.py /
COPY test.py /
COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]