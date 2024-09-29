FROM python:3-alpine

RUN set -uex && \
    pip install docker Faker

WORKDIR /src

ENTRYPOINT [ "python" ]
CMD [ "-m", "healer", "-v" ]

ADD ./src /src
