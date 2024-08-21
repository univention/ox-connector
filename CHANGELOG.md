# Changelog

## [0.12.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.11.0...v0.12.0) (2024-08-21)


### Features

* **ox-connector:** migrate OX connector-standalone to Provisioning service ([e92d87f](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/e92d87fc33eb011822516c66ec41f59f02cec2bf)), closes [univention/customers/dataport/team-souvap#369](https://git.knut.univention.de/univention/customers/dataport/team-souvap/issues/369)

## [0.11.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.10.0...v0.11.0) (2024-08-14)


### Features

* added content for the data-loader ([aa81c11](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/aa81c11a0b35a6d022d86081a22e4e17eb752732))


### Bug Fixes

* qa fixes ([4d236d5](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/4d236d546a0cf83c18cd5189ec25efe1268d0656))

## [0.10.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.9.1...v0.10.0) (2024-07-02)


### Features

* **helm/ox-connector:** Add extraVolumes and extraVolumeMounts template ([8ed72f6](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/8ed72f6db6ab8705a5cc4f2601dc8ca6550baad9))

## [0.9.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.9.0...v0.9.1) (2024-06-28)


### Bug Fixes

* change loader script ([3f116c9](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/3f116c96fc040e1e32445753452f63fa3a50997c))
* fixup typo ([7047857](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/7047857e48e5be85ca1c59c2e476b2e9b5b05a9b))
* fixup! remove wrong paths ([1bbb2d9](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/1bbb2d9e080569f46b15bf00ec18d6b03ed7c2b8))

## [0.9.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.8.2...v0.9.0) (2024-06-25)


### Features

* Migrate images to harbor ([3eca01d](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/3eca01d34dc701bf69547717a1160cccf3251c61))
* Move extensions image from ox-connector-extensions to ox-extension ([f3a5ef6](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/f3a5ef63fb9b0454ea22d6e61c2cb37facba8d4e))


### Bug Fixes

* package ldap schemas and udm extensions ([5e1a3ab](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/5e1a3ab211326e8f24b4e6896dcbb11b0009a504))
* unify loader script to the rest of containers plugin loaders ([ad0633a](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/ad0633a1bba0ff1bb73de44df2ba18f9d9619f52))

## [0.8.2](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.8.1...v0.8.2) (2024-05-22)


### Bug Fixes

* Fix the context removal process ([5c27927](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/5c27927fc2ac3d2c5861f4c881971dbbdf573457)), closes [univention/dev-issues/dev-incidents#2](https://git.knut.univention.de/univention/dev-issues/dev-incidents/issues/2)

## [0.8.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.8.0...v0.8.1) (2024-04-26)


### Bug Fixes

* performance ([f308aa2](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/f308aa2b2bcd6e17437c2dc0c9b313edb50c0e7a))

## [0.8.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.7.1...v0.8.0) (2024-04-12)


### Features

* add attribute mapping configuration to user sync ([c3997e5](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/c3997e5361580ad3984893268fcc14378a5b9138)), closes [#55861](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/55861)

## [0.7.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.7.0...v0.7.1) (2024-01-18)


### Bug Fixes

* **docker/standalone:** update ucs-base from 5.0-5 to 5.0-6 ([e39e3b6](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/e39e3b6c311cfffd315ddbeb2eb9f8405cc7bb5e))

## [0.7.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.6.4...v0.7.0) (2024-01-18)


### Features

* **ci:** add debian update check jobs for scheduled pipeline ([93eccd0](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/93eccd0a17b5e67558b696b57a5f872f34d3030f))
* **ci:** add debian update check jobs for scheduled pipeline ([9121c20](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/9121c2012414c7a81e1afd2718edbdacd2ee9959))

## [0.6.4](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.6.3...v0.6.4) (2024-01-17)


### Bug Fixes

* **tests:** fix wait-for-listener timing issues ([805b4bd](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/805b4bd3aa9d79c938b93bf7c7fb196ceb9a1225))

## [0.6.3](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.6.2...v0.6.3) (2024-01-16)


### Bug Fixes

* **functional_account:** Correct escape sequence '\w' ([94b2f2c](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/94b2f2c059d84821b95d874601e4e3eb70faae73))
* **functional_account:** Replace undefined variable 'INVALID_FORMAT_ERR_MSG' ([045595b](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/045595bc81e70f9cd6e203a8f8f054232425268d))

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
