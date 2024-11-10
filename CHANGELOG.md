# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2024-11-10

## Fixed

- Change tag name pushed via GitHub Actions

  SemVer tags were pushed in numerical format (e.g.: 1.1.0) while the released
  compose file was using prefixed format (e.g.: v1.1.0).

## [1.1.0] - 2024-10-20

### Added

- Add customization for target container label

  Target container will be managed if the default 'healme' label or any custom
  label (configured via 'HMD_CONTAINER_LABEL' environment variable) is attached.

## [1.0.0] - 2024-10-06

### Added

- Add first implementation.

[1.1.1]: https://github.com/ioriomauro/healmydocker/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/ioriomauro/healmydocker/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ioriomauro/healmydocker/releases/tag/v1.0.0
