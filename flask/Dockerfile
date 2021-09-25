FROM alpine:3.12.3

ENV PYTHONUNBUFFERED=1 \
    APP_ROOT_PATH=/src \
    SERVER_PORT=10080 \
    LD_LIBRARY_PATH=/opt/vc/lib

# install python
RUN    apk --no-cache update \
    && apk --no-cache add bash tzdata python3 raspberrypi-libs tini \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && ln -sf python3 /usr/bin/python \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --no-cache --upgrade pip setuptools wheel \
    && ln -sf pip3 /usr/bin/pip \
    && mkdir -p ${APP_ROOT_PATH} \
    && rm -rf /root/.cache /var/cache/apk/*

# install package
COPY requirements.txt /requirements.txt
RUN    apk add --no-cache --virtual .build-deps \
                          gcc musl-dev libffi-dev g++ libgcc libstdc++ \
                          libxslt-dev python3-dev libc-dev linux-headers \
    && pip3 install -r /requirements.txt --extra-index-url https://www.piwheels.org/simple \
    && apk --purge del .build-deps \
    && rm -rf /root/.cache /var/cache/apk/*

# add prompt file
COPY color_prompt.sh /etc/profile.d/color_prompt.sh
RUN echo "source /etc/profile" >> /root/.bashrc

WORKDIR ${APP_ROOT_PATH}

CMD ["/usr/bin/python", "app.py"]
