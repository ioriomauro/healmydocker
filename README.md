# HealMyDocker

A docker-ized container autohealer.

Simple python program that attaches to docker socket and listens for docker
'health_status' events and restarts labeled containers when they become
unhealthy.

> TBD: here go badges

## Table Of Contents

- [HealMyDocker](#healmydocker)
  - [Table Of Contents](#table-of-contents)
  - [Background](#background)
  - [Install](#install)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [Security](#security)
  - [Contribute](#contribute)
  - [Maintainers](#maintainers)
  - [License](#license)

## Background

[Docker][4] is a modern way to run your applications in a kind of *sandbox*
called "container". Containers can be healthy (when they run smoothly providing
the service they are meant to) or unhealty (the main process, subprocesses or
threads are unable to run correctly and the service is degraded or not
provided at all), and developers are encouraged to provide [healthchecks][5] for
their containers. Unfortunately there's no automagic built-in feature that will
"heal" an unhealthy container. At least *not yet*.

HealMyDocker is an application, shipped as container image, that runs in docker,
listens to the docker socket and waits for [health_status][6] events; when
a running container is marked `unhealthy`, HealMyDocker will notice and will
restart it, hoping that it will be running correctly again.

This project is indented to be used by docker application developers, system
administrators, DevOps, SysOps, and whoever may need a simple auto-restart
tool for their unhealty containers.

This is NOT a *6th-Level Evocation Heal spell*; if your container has problems
that cannot be resolved by a simple restart (e.g.: software bugs, broken
network, misconfiguration...) nothing will change upon restart and it will
start malfunctioning again.

## Install

To use this project you'll need an already installed and running docker daemon.
Please refer to [GetDocker][7] for all the instructions.

## Configuration

HealMyDocker need to attach to docker socket (usually `/var/run/docker.sock`)
on the host machine. Il will subscribe to system events, filtering for
`health_status`, and will react to `unhealthy` events if and only if the
marked container has the correct label with the correct value. The default
label name is `healme` and the value MUST be as in the following example:

> healme: true

Starting from version 1.1.0, container label can be customized with the
`HMD_CONTAINER_LABEL` environment label. For example with:

```shell
    docker run \
        -e HMD_CONTAINER_LABEL=healmyapp \
        ioriomauro/healmydocker:latest
```

you can attach the label `healmyapp=true` (pun intended) to your app container.

Different label values or any other labels applied to the target container
will cause HealMyDocker to ignore the event and continue.

HealMyDocker runs independently from the machine Timezone, so no further
configuration is required.

## Usage

There are three ways to run HealMyDocker.

1.  Docker CLI

    ```shell
    docker run --rm -d \
        --name healmydocker \
        --restart=always \
        --network=none \
        -v /var/run/docker.sock:/var/run/docker.sock \
        ioriomauro/healmydocker:latest
    ```

    This is the simplest way. It will run HealMyDocker as a standalone,
    ephemeral container, in detached mode, with no network, mounting the host
    docker socket to it.

2.  docker-compose standalone

    ```yaml
    services:
      healmydocker:
        container_name: healmydocker
        image: ioriomauro/healmydocker:latest
        network_mode: none
        restart: always
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
    ```

    This will simplify deployment and management; just copy the compose file
    to the host machine and launch `docker-compose up -d`.

    NOTE: the sample yaml file assumes that the docker socket is in the default
    path on the host machine.

3.  Integrate in your docker-compose project

    ```yaml
    services:
      app:
        image: my/app:latest
        ...
        labels:
          healthisapp: true

      healmydocker:
        image: ioriomauro/healmydocker:latest
        environment:
            - HMD_CONTAINER_LABEL=healthisapp
        network_mode: none
        restart: always
        volumes:
          - /var/run/docker.sock:/var/run/docker.sock
    ```

    Assuming that your application already runs in compose, just add the
    `healmydocker` service to it.

Please note that all the examples fetch the `latest` image from the registry.
This is not recommended for production environments; latest image is built and
pushed in CI without major testing, while [semver][8] tags are fully tested.
Please stick to a `major` or `major.minor` version for production environments.
For example you can safely use something like:

> docker run -d `ioriomauro/healmydocker:1.0`

or

> docker run -d `ioriomauro/healmydocker:1`

Last but not least, in order to leverage HealMyDocker features, you must label
your container as shown in [Configuration](#configuration).

## Security

HealMyDocker container runs with standard privileges and no network (as it
has no needs to communicate with other containers or the host); it has read/write
access to the docker socket, but it only listens for docker events and issue
restart commands for unhealthy containers, and periodically pings the daemon
for heartbeating purposes.

## Contribute

Please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) file for information
about how to get involved. We welcome issues, questions, and pull requests.

## Maintainers

- Mauro Iorio: iorio (dot) mauro (at) TheBigGMail (dot) com

## License

This project is licensed under the terms of the [LGPL-3.0-only][1] open source
license. Please refer to [COPYING](./COPYING) and
[COPYING.LESSER](./COPYING.LESSER) for the full terms.

---

The template for this [readme][2] file is Copyright © 2021 Yahoo Inc., licensed
under [CC-BY-4.0][3].

[1]: https://www.gnu.org/licenses/lgpl+gpl-3.0.txt "GNU LESSER GENERAL PUBLIC LICENSE 3"
[2]: https://yahoo.github.io/oss-guide/docs/publishing/publishing-template/Spec-READ-AND-DELETE.html#open-source-skeleton-template "Open Source Skeleton Template"
[3]: https://creativecommons.org/licenses/by/4.0/legalcode "Creative Commons Attribution 4.0 International"
[4]: https://www.docker.com "docker.com"
[5]: https://docs.docker.com/reference/dockerfile/#healthcheck "Dockerfile HEALTHCHECK"
[6]: https://docs.docker.com/reference/cli/docker/system/events/ "Docker System Event"
[7]: https://docs.docker.com/get-started/get-docker/ "Get Docker"
[8]: https://semver.org "Semantic Versioning 2.0.0"
