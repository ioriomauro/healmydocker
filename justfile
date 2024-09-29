_default:
    @just --list --unsorted

devel:
    docker compose build
    docker compose run --rm --entrypoint sh devel

python:
    docker compose build
    docker compose run --rm --entrypoint python devel

up:
    docker compose up --build --force-recreate

test:
    docker compose build
    docker compose run --rm --entrypoint python devel -m unittest -v
