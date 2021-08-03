FROM pajikos/sms-gammu-gateway AS base

ENV BASE_PATH /sms-gw
WORKDIR $BASE_PATH

COPY runha.sh $BASE_PATH
COPY runha.py $BASE_PATH
COPY runnomodem.py $BASE_PATH
COPY gammu.config $BASE_PATH

RUN apk add --no-cache bash
RUN apk add --no-cache curl
RUN apk add --no-cache jq

COPY bashio/lib /usr/lib/bashio

RUN ln -s /usr/lib/bashio/bashio /usr/bin/bashio

CMD [ "./runha.sh", "" ]
