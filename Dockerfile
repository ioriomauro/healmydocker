FROM python:3-alpine

ARG VERSION

LABEL maintainer="Mauro Iorio <iorio.mauro@gmail.com>"

RUN set -uex && \
    pip install docker Faker

WORKDIR /src

ENV HMD_CONTAINER_LABEL='healme'

ENTRYPOINT [ "python" ]
CMD [ "-m", "healer", "-v" ]

LABEL version="${VERSION}"
ADD ./src /src
