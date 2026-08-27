ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-evdev py3-requests

# Kopiere das services.d-Verzeichnis
COPY services.d /etc/services.d/
# Stelle sicher, dass das Dienstskript ausführbar ist
RUN chmod +x /etc/services.d/power-button/run
RUN chmod +x /etc/services.d/power-button/finish

#COPY run.sh /
#RUN chmod a+x /run.sh

COPY power_button.py /
RUN chmod +x /power_button.py



#CMD [ "/run.sh" ]