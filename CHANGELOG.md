# Changelog

## [0.6.2](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.6.1...v0.6.2) (2024-01-16)


### Bug Fixes

* **tests:** fix test_cache errors ([3fd8eb1](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/3fd8eb10beb76b658c26e0dcb6fdc4e8341f256f))

## [0.6.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.6.0...v0.6.1) (2024-01-15)


### Bug Fixes

* **deps:** add renovate.json ([417a472](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/417a4729c29e370f07ab9105cb255db353b91e32))

## [0.6.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.5.0...v0.6.0) (2024-01-12)


### Features

* debug tool for data consistency ([37133f0](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/37133f09e152cf894bc24bc0338a4ae1f055d386)), closes [#56526](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/56526)

## [0.5.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.4.4...v0.5.0) (2024-01-11)


### Features

* **app-settings:** add app settings OX_USER_IDENTIFIER and OX_GROUP_IDENTIFIER ([724675a](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/724675a7e2da8e3dc0bf6206907c7fd19ba97436)), closes [#56881](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/56881)


### Bug Fixes

* remove "set -o nounset" from all scripts ([4f3d180](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/4f3d180eab524006ed75311959edc1e94b0c5b09)), closes [#56946](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/56946)
* typo in app/uinst ([14e170f](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/14e170ffbc107468eaaf122b2bba35694cd745c0)), closes [#56959](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/56959)
* use sh for scripts that run inside the container ([9ba0485](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/9ba0485c7c034d89332ff9d86c0199f5db9a01bf)), closes [#56958](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/56958)

## [0.4.4](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.4.3...v0.4.4) (2024-01-02)


### Bug Fixes

* **ci:** use <appcenter-version>-dev on non-default branches ([5ef6f09](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/5ef6f09ce387f2316e396162a0538753ca3ec4db))

## [0.4.3](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.4.2...v0.4.3) (2023-12-28)


### Bug Fixes

* **licensing/ci:** add spdx license headers, add license header checking pre-commit ([7756466](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/7756466fbacdbc45a6d3ba483544b434f5c77075))

## [0.4.2](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.4.1...v0.4.2) (2023-12-18)


### Bug Fixes

* **ci:** add Helm chart signing and publishing to souvap via OCI, common-ci 1.12.x ([48f069c](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/48f069c4a36488c00cfdee492c3e90e6bdc78039))

## [0.4.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.4.0...v0.4.1) (2023-12-15)


### Bug Fixes

* **ci:** correct build-image-path ([cb0bb8e](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/cb0bb8e394ffe0897b2525826ca5688fb3f1622f))

## [0.4.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.3.5...v0.4.0) (2023-12-14)


### Features

* save filename and message error on exceptions ([7cf95ee](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/7cf95ee94d97e69b6803374af3d99f436fd35825))


### Bug Fixes

* **ci:** reference common-ci v1.11.x to push sbom and signature to souvap ([38382ba](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/38382ba4a3498754a78e223d2c7baa465598204a))
