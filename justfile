compose_project_name := "healmydocker"
public_repo := "ioriomauro/" + compose_project_name
sem_ver := `sed -E -e 's/.*(v\\d+\\.\\d+\\.\\d+).*/\\1/g' <VERSION`


_default:
    @just --list --unsorted

_build:
    docker compose build --pull --build-arg VERSION="{{sem_ver}}"

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
        --pull \
        --build-arg VERSION="{{sem_ver}}" \
        --platform 'linux/amd64,linux/arm64,linux/arm/v6,linux/arm/v7' \
        --tag "{{public_repo}}:latest" \
        --tag "{{public_repo}}:{{sem_ver}}" \
        .
    docker image push --all-tags "{{public_repo}}"

scout: _build
    docker scout quickview {{compose_project_name}}-devel:latest

update-reference:
    #!/usr/bin/env bash
    cat <<EOF | sed -E -e 's#(image: {{public_repo}}):.*#\1:{{sem_ver}}#g' >reference/docker-compose.yml
    services:
      healmydocker:
        container_name: healmydocker
        image: ioriomauro/healmydocker:latest
        network_mode: none
        restart: always
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
    EOF
