FROM ghcr.io/home-assistant/aarch64-base:latest

RUN apk add --no-cache stress-ng

COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]