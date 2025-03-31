# Changelog

## [0.19.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.18.1...v0.19.0) (2025-03-31)


### Features

* OX-Connector 2.3.0 ([415ea8b](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/415ea8b426a8817018039668d6cef6ce0a18aaed)), closes [univention#891](https://git.knut.univention.de/univention/univention/issues/891) [#58059](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/58059) [univention/prof-services/team-enterprise/zit-sh#72](https://git.knut.univention.de/univention/prof-services/team-enterprise/zit-sh/issues/72) [univention/prof-services/team-enterprise/zit-sh#69](https://git.knut.univention.de/univention/prof-services/team-enterprise/zit-sh/issues/69)


### Bug Fixes

* do not log all error cases ([658dcb8](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/658dcb87b5f65cb1e6bad30b177b7ac87dcfeb7a)), closes [univention/open-xchange/provisioning#109](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/109)
* improve log messages ([d6a708e](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/d6a708e9de2f7357ec36c36c874335a44b3c548e)), closes [univention/open-xchange/provisioning#109](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/109)

## [0.18.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.18.0...v0.18.1) (2025-03-28)


### Bug Fixes

* Recover from inconsistent state after moving a user failed. ([06d8349](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/06d8349f469e60bd333f38dbe4fa7154e59f929c)), closes [univention/open-xchange/provisioning#109](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/109)

## [0.18.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.17.1...v0.18.0) (2025-03-27)


### Features

* include i18n translations in ox-extension image ([ec5b7e2](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/ec5b7e2f33494990f4ffbec27e12c75ce11cf22e)), closes [univention/dev/internal/team-nubus#1048](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1048)
* include i18n translations in ox-extension image / enabled multi stage build ([1715d64](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/1715d6477f7da955483ed1e8c5febdb14751d03a)), closes [univention/dev/internal/team-nubus#1048](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1048)

## [0.17.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.17.0...v0.17.1) (2025-03-27)


### Bug Fixes

* ox-connector standalone image build fix ([035b107](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/035b107ec3fc8695f7eca11be092638dfa8307d4))

## [0.17.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.16.1...v0.17.0) (2025-02-26)


### Features

* Bump ucs-base-image to use released apt sources ([40bb712](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/40bb712322349834f176315284481e4a34a264bf))

## [0.16.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.16.0...v0.16.1) (2025-02-17)


### Bug Fixes

* handle dn case insensitive for old db ([65d7ddb](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/65d7ddb47497bf87269de3f546b9da05fb9d6b20))

## [0.16.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.15.1...v0.16.0) (2025-02-14)


### Features

* added system user creation and portal tile creation ([38dc86b](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/38dc86b9281d01c0bc76e781f6a50e1619961a25))


### Bug Fixes

* add OX Context to UMC policies ([da27141](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/da27141a8a05809758ad9a487f75f635abea129c))
* **ox-extension:** Add functional accounts icon ([a6379cb](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/a6379cb95fc19ef14edeacc8abc69b1bcea67bd6))
* **ox-extension:** Prepare to add translation file ([5e4cc53](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/5e4cc53f6319130c23127a41cdbdbd9efbbade8a))
* remove tiles not needed ([bc5262b](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/bc5262b0e183a9e9ff2b885e9a8622a66186af70))

## [0.15.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.15.0...v0.15.1) (2025-02-10)


### Bug Fixes

* add .kyverno to helmignore ([70b5724](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/70b57244cde9e9f934aa0ea162be81ccee479813))
* **docs:** Password setting requirement in OX Connector ([0fe8a24](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/0fe8a24e3dd9dcccfc1d9fd49f463019f116b353)), closes [univention/open-xchange/provisioning#103](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/103) [#57908](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/57908)

## [0.15.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.11...v0.15.0) (2024-12-20)


### Features

* upgrade UCS base image to 2024-12-12 ([4395288](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/4395288f1cdff99f362625daebc67bdad0bfdbaf))

## [0.14.11](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.10...v0.14.11) (2024-12-16)


### Bug Fixes

* hotfix typo in values ([44aea1b](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/44aea1b7133163680f96c51e57b25e431727c69f))

## [0.14.10](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.9...v0.14.10) (2024-12-10)


### Bug Fixes

* kyverno lint for ox-connector ([a3e3315](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/a3e33150bee2faaf9812ec19e6015e7063096b76))

## [0.14.9](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.8...v0.14.9) (2024-12-02)


### Bug Fixes

* ci malware scan configuration ([c96795e](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/c96795e9092014a220d76f6edef16f3543b4e7c1))

## [0.14.8](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.7...v0.14.8) (2024-11-28)


### Bug Fixes

* kyverno lint ([122fd61](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/122fd6196e4bc9f9b31cbbcd157e9d8eb2eac568))
* **listener:** better error message in case old json is missing ([af9a11b](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/af9a11baf3f49febc20a997bebc199b8c4c0176c)), closes [univention/open-xchange/provisioning#97](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/97)
* malware scan CI configuration ([fddd4af](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/fddd4afc1741f12a72187b3db850f7c645f78dad))
* probes ([56ae9ed](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/56ae9ed4c30e80746fc54c352b5076036013178d))
* simplify statefulset template ([36dbb7f](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/36dbb7f6d4ddee00348b52060985a878725f8a94))
* **soap backend:** better error message in case identifier is None ([a485ee5](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/a485ee5f1eb51f948dd46ecf4027f0e1ebcb35c8))

## [0.14.7](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.6...v0.14.7) (2024-10-29)


### Bug Fixes

* **changelog:** change release date ([dfaa982](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/dfaa982cf312fb302ef7bfc2c4a4914999b95a54))

## [0.14.6](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.5...v0.14.6) (2024-10-24)


### Bug Fixes

* **accessprofile:** support special characters in accessprofile name and ([f7790f3](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/f7790f3ccaba197d28f842f4e39d9a8226c0bfaa)), closes [univention/open-xchange/provisioning#100](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/100)

## [0.14.5](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.4...v0.14.5) (2024-09-26)


### Bug Fixes

* bump Provisioning client version, adapt to new subscriptions format ([c168455](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/c1684557fe797175ed7fead9a7d02fc749949d7c))

## [0.14.4](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.3...v0.14.4) (2024-09-24)


### Bug Fixes

* bump Provisioning client version, adapt to new endpoint names ([8004f74](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/8004f748d861555e43cea3ca84629d5af4bb624e))

## [0.14.3](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.2...v0.14.3) (2024-09-19)


### Bug Fixes

* consumer path and provisioning debugging ([aec02eb](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/aec02ebc4dde53dc0dbfd40680d8fe1d16eebb2c))

## [0.14.2](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.1...v0.14.2) (2024-09-18)


### Bug Fixes

* update nubus-provisioning-consumer and ox-connector-appcenter image tag ([b825e4b](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/b825e4b251039bca9465722c255540e443f61c64)), closes [univention/customers/dataport/team-souvap#811](https://git.knut.univention.de/univention/customers/dataport/team-souvap/issues/811)

## [0.14.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.14.0...v0.14.1) (2024-09-16)


### Bug Fixes

* set default_sender_address to primary_email during user modify if primary_email changed and was the former default_sender_address (Issue univention/open-xchange/provisioning[#96](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/96)) ([cef9178](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/cef9178561445bcd8c3bc80862cd78cf8fb00722))

## [0.14.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.13.0...v0.14.0) (2024-09-16)


### Features

* update UCS base image to 2024-09-09 ([88fc913](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/88fc9134e3a089c7bcb41575e930bc8abbbfbbe4))
* upgrade docker standalone UCS base to 5.2-0 ([8b2c2cf](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/8b2c2cf944df08de7f2788483cc081ddcc604cc1))
* upgrade wait-for-dependency ([653229c](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/653229c7ea589a423add56bcc0b03a161169fd7e))

## [0.13.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.12.0...v0.13.0) (2024-08-27)


### Features

* **ox-connector:** Default containers for functional accounts ([034d808](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/034d808eb69f25726ccbddcfb25885efffabd550)), closes [univention/open-xchange/provisioning#95](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/95)

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
