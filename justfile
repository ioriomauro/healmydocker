public_repo := "ioriomauro/healmydocker"
sem_ver := `sed -E -e 's/.*(v\\d+\\.\\d+\\.\\d+).*/\\1/g' <VERSION`


_default:
    @just --list --unsorted

_build:
    docker compose build --build-arg VERSION="{{sem_ver}}"

shell: _build
    docker compose run --rm --entrypoint sh devel

python: _build
    docker compose run --rm --entrypoint python devel

up:
    docker compose up --build --force-recreate

down:
    docker compose down -v

devel:
    docker compose watch

test: _build
    docker compose run --rm --entrypoint python devel -m unittest -v

publish: test
    # Assumes that the current builder supports multi-platform images
    docker buildx build \
        --platform 'linux/arm64,linux/amd64' \
        --tag "{{public_repo}}:latest" \
        --tag "{{public_repo}}:{{sem_ver}}" \
        .
    docker image push --all-tags "{{public_repo}}"
