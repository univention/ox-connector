# Changelog

## [0.34.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.33.2...v0.34.0) (2025-12-10)


### Features

* **helm:** Add component-specific extraEnvVars support ([a2e63bd](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/a2e63bdab031e488218b651e817ab97cdab141f3)), closes [univention/dev/internal/team-nubus#977](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/977)

## [0.33.2](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.33.1...v0.33.2) (2025-12-10)


### Bug Fixes

* **deps:** Update dependency univention/dev/nubus-for-k8s/common-ci to v1.54.0 ([bb91690](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/bb91690d470e76c3c1260b5ef026e54830c9404a)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.33.1](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.33.0...v0.33.1) (2025-12-03)


### Bug Fixes

* bump image to errata 298 ([eaec7b2](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/eaec7b25a0a522306f9bd8e8b48c3293e85e4ae4)), closes [univention/dev/internal/team-nubus#1543](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1543)

## [0.33.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.32.4...v0.33.0) (2025-11-28)


### Features

* update to use large-groups version of nubus-provisioning-consumer ([4410a6f](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/4410a6f5856ec21a5a23f244249addca4e5a8963)), closes [univention/dev/projects/open-xchange/connector#143](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/143)
* use prod Dependency-Track URLs ([a6650b6](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/a6650b6027ff2ee7a9c7679122316a2a50a6769b)), closes [univention/dev/internal/team-nubus#1512](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1512)


### Bug Fixes

* Add vulnerability scanning pipeline jobs to the Gitlab CI ([52af181](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/52af181e49d9b1946bf7033d33bad3247fa47c99)), closes [univention/dev/internal/team-nubus#1471](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1471)
* bump wait-for-dependency image. ([969797a](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/969797a2dc5209b2551a9983fa750dc2f1cd8aaf)), closes [univention/dev/internal/team-nubus#1476](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1476)
* ci: vul-man SBOM upload cleans tag before uploading new SBOMs for a tag ([5946e18](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/5946e18daa7b6e7f2e77df4310ada1bdaa24fb61)), closes [univention/dev/internal/team-nubus#1529](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1529)
* **ci:** Bump common-ci ([ab06a22](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/ab06a220388e3e75476fd6c60ce27fd6e0d6bf08)), closes [univention/dev/internal/team-nubus#1532](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1532)
* **ci:** Disable sonarqube it is broken and shadows errors of the vulnerability scan ([0c26639](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/0c266395aade01680cb5b4a1044232fa7ab96bbd)), closes [univention/dev/internal/team-nubus#1471](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1471)
* **ci:** Failing test with securityContext enabled ([54becc0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/54becc0529af09321b4ad6b51d48c9ce46c5f7dd)), closes [univention/dev/internal/team-nubus#1522](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1522)

## [0.32.4](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.32.3...v0.32.4) (2025-11-17)


### Bug Fixes

* **ox-connector k8s:** Add unit test testing if normalized DNs are stored in the DB ([4325407](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/4325407351a0b1dd6054448073148e328dc37289)), closes [univention/dev/internal/team-nubus#1482](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1482)
* **ox-connector k8s:** Normalize DNs and migrate existing databases ([88cd3df](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/88cd3df0fa7f265a96f453b191d2f2df591bcf30)), closes [univention/dev/internal/team-nubus#1482](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1482)
* **ox-connector k8s:** Use resources from main container for migration init container ([8c81ba9](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/8c81ba95fce294200c005095a595cef52ca9be4b)), closes [univention/dev/internal/team-nubus#1482](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1482)

## [0.32.3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.32.2...v0.32.3) (2025-11-04)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.3-build.20251030 ([7923e4a](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/7923e4a6ae335f887669305c6b45225eb7eb6a69)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.32.2](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.32.1...v0.32.2) (2025-10-30)


### Bug Fixes

* trigger release and update DEPUTY_PERMISSION.md ([8178a12](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/8178a12816984bb24aa0bb4f9f32b6c4c8a54e06)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.32.1](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.32.0...v0.32.1) (2025-10-29)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.3-build.20251024 ([4666bdc](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/4666bdc92cc05e3d5655e3f88d26a7e72ff4c64e)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.32.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.31.0...v0.32.0) (2025-10-28)


### Features

* Add logging to support tests ([ec73b36](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/ec73b36953656afc927534dbaa7527370dbeb467)), closes [univention/dev/internal/team-nubus#1369](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1369)


### Bug Fixes

* Correct copying of updated / changed dependencies ([4db680c](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/4db680c71ac7db6605da68b23f52088ee3fc7c55)), closes [univention/dev/internal/team-nubus#1369](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1369)
* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.3-build.20251023 ([d9cdc05](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/d9cdc05e5ad83c87b7e831748c94794044914a71)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)
* **docs/packaged-integration:** Value of oxDefaultContext from string to integer ([1ebeae7](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/1ebeae7e7b817c05e232978466327aa4cfabe1f2)), closes [univention/dev/projects/open-xchange/connector#141](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/141)

## [0.31.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.30.2...v0.31.0) (2025-10-17)


### Features

* Move "TriggerObject" into a new models module ([f57a88a](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/f57a88ac5c91139f3a24bcfad458c931cd00ff73)), closes [univention/dev/internal/team-nubus#1369](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1369)


### Bug Fixes

* adjust test_converting_ox_user_to_non_ox_user_updates_cache_correctly test ([a4f179d](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/a4f179d542ff5f18a3a1239292cc3f75039e4bab)), closes [univention/dev/internal/team-nubus#1369](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1369)

## [0.30.2](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.30.1...v0.30.2) (2025-10-14)


### Bug Fixes

* **ox-connector:** Correct retrieval of the ID from the task file when deleting an object ([955b1cc](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/955b1cc24a23d310712c915ba9c7eefc93df7193))

## [0.30.1](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.30.0...v0.30.1) (2025-10-14)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.3-build.20251009 ([2c178a5](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/2c178a5b32d70f04030af76b56e0bcbd7735e8cd)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.30.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.29.0...v0.30.0) (2025-10-09)


### Features

* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#136](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/136) - Improve CLI tool univention-ox-connector-task-management ([eeeef8a](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/eeeef8aa1ecb290ba7001679eef0287d487ea799))

## [0.29.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.7...v0.29.0) (2025-09-30)


### Features

* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Add simple script to manage DB ([b548d4c](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/b548d4c6192f74073816188ea1d0e8cbf4ed3f9b))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Correct DockerImage name ([246d721](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/246d721e9cea70cdade68d7f55dec3c79e6fc358))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Documentation ([4240801](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/4240801ab0a6e7888a3e7430c9a564bdcbbca117))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Documentation for 3.0 (WIP) ([bdccfca](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/bdccfca3a0ee17d93895f07dfc3f4c9d8f47c922))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - First iteration ([d635ac4](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/d635ac47fa97aeabdc5cd98a658fbae367eaf86c))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Fix Linting ([618f6a5](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/618f6a55bf3262d81cbd09bc0b95bf13c6085e56))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Fix new database name ([f8a59de](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/f8a59deb0dd3aa6d75696e9a6d5a1ed8a548a114))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Fix tests ([2baac92](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/2baac9224b3c0ec3e024cb8abac8fc20fe0a51f0))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Hide the new behavior behind a feature flag, switch to SQLite ([a5985a3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/a5985a377bdbaedc5b7cf3be8e047b5d77368e73))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Improve group resync ([0eed72a](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/0eed72a9f0abdb9a124e733007c65b973d01d91e))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Move to UCS 5.2 ([fc41eb3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/fc41eb32e4ab0bcfdc54f8501a4dd4a6a95be57a))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - New error handling for the OX Connector in UCS ([c490f03](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/c490f03dbbcfc0ebec51c81f1d2a8a1b30e4f071))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - README_UPDATE ([b7164bb](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/b7164bb12c1bea593cfaca588ebb379e640de209))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Remove from error table after successful move to old ([d341970](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/d341970c8a1a9df46b5791f1a1ea48d430687b88))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Spelling ([df58e3c](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/df58e3c4634008081f808f5e3f40a566f3aea290))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - Spelling ([7adc103](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/7adc103de5f48993e2352a15a1431522da18405d))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) - SQLite instead of Postgres, improved output of filter_error, added show_task_summary ([0e29cc7](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/0e29cc72c154e0d68609c0498f18eb159b22b331))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135) adjust usability of diagnostic tool ([56e5be9](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/56e5be94f3b6ed9b46de3b0f687b4f41b334e392))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135): Add exceptions that should stop the connector ([7c194b8](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/7c194b860cd53b745f1d5d3a6ee406ab54f5ea87))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135): Better usability ([767cd00](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/767cd0018c43c654a6f5c4a953820c396b6b8fa2))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135): Fix boolean script arguments ([767005f](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/767005fe1c9dd37947122d7abc861d47caf3082e))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135): fix upgrade path ([68a3fbc](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/68a3fbce93c4e5825e5c4f7415db0484d8bb1dad))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135): fix upgrade path ([532f92a](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/532f92ae8b48f37270ab23915cd8f4d08e27b164))
* **error-handling:** Issue univention/dev/projects/open-xchange/connector[#135](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/135): More coherent wording, also in documentation ([555ed88](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/555ed88f322f5c89109517328be1fdfd7459ee2b))


### Bug Fixes

* deputy permissions on k8s ([ebbfc91](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/ebbfc9181f3b1b80ad799c107c2bc73cf596c94e)), closes [univention/dev/internal/dev-issues/dev-incidents#153](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/153)

## [0.28.7](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.6...v0.28.7) (2025-09-29)


### Bug Fixes

* Kyverno lint issues ([425dbc7](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/425dbc71ed28e4c0dd4dc808a7fb573710ee463a)), closes [univention/dev/internal/team-nubus#1426](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1426)

## [0.28.6](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.5...v0.28.6) (2025-09-27)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/common-helm/testrunner Docker tag to v0.26.1 ([751bc3b](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/751bc3b76ed8b0a22eb3d118bd0a848b5460c8a5)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.28.5](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.4...v0.28.5) (2025-09-25)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.3-build.20250923 ([227679f](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/227679f72e7026de9f27cf234cac2d4bfa9297a3)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.28.4](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.3...v0.28.4) (2025-09-23)


### Bug Fixes

* Remove call to apt-get update ([2ea59b9](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/2ea59b94df15b0adb2941f337b01e84f7f168754)), closes [univention/dev/internal/team-nubus#1377](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1377)
* Remove the cleanup of APT data ([3a55318](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/3a55318efd6a2e8ca1399b20db47d49ec134da97)), closes [univention/dev/internal/team-nubus#1377](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1377)

## [0.28.3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.2...v0.28.3) (2025-09-15)


### Bug Fixes

* lint issues ([af4ffc9](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/af4ffc9d2c46072d5465d27da8db7ed87ee760d7)), closes [univention/dev/internal/team-nubus#1368](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1368)
* missing security context ([5309499](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/53094993dbe67f97c0d92dfbc883f5c8cd3ff245)), closes [univention/dev/internal/team-nubus#1368](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1368)

## [0.28.2](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.1...v0.28.2) (2025-09-12)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.3-build.20250911 ([a104467](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/a10446726dbd5d6f528af89e0dcb2f864ac75080)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.28.1](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.28.0...v0.28.1) (2025-09-12)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.3-build.20250909 ([8f03c71](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/8f03c71d2a2ccf429236516912bb157923715a0d)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.28.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.12...v0.28.0) (2025-09-11)


### Features

* **helm:** Adjust handling of "provisioningApi.auth" ([336f71e](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/336f71eff3aa040964d46e1c30156c84e5f332c6)), closes [univention/dev/internal/team-nubus#1094](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1094)
* **helm:** Migration required: Adjust handling of oxConnector secrets ([b9c4a53](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/b9c4a53e4b4d60c4c71ac85fee6c6c71edc7d707)), closes [univention/dev/internal/team-nubus#1094](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1094)
* **helm:** Migration required: rename oxConnector to openXchange ([e8a1a37](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/e8a1a3728e2abbf33085bcd6143c6056f77ae196)), closes [univention/dev/internal/team-nubus#1094](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1094)

## [0.27.12](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.11...v0.27.12) (2025-09-11)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/common-helm/testrunner Docker tag to v0.24.5 ([95177e6](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/95177e6f78f597ddc546a11b3ec701788aa65565)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.27.11](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.10...v0.27.11) (2025-09-11)


### Bug Fixes

* Configure fsGroup so that the container starts up with the defaults ([27c7b12](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/27c7b12e5c8e4283778c59f035fc1f66955e7123)), closes [univention/dev/internal/team-nubus#1377](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1377)

## [0.27.10](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.9...v0.27.10) (2025-09-05)


### Bug Fixes

* **helm:** Allign helm image configuration with the nubus standards ([10c16ab](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/10c16ab17554395e592bf128c3e0dc37169c667b))
* **helm:** delete hpa config because the ox-connector can only be deployed once ([bdd9244](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/bdd9244ffc991a8d87a48c6daf9502b83237a911))
* **helm:** fix helm annotations templating ([23dcc95](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/23dcc95e58904ccc3663bf15656696ae37920bd8))

## [0.27.9](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.8...v0.27.9) (2025-09-05)


### Bug Fixes

* **deps:** Update dependency univention/dev/nubus-for-k8s/common-ci to v1.44.2 ([09145b8](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/09145b8e236ee180f570a054a7c8c3c20d185b14)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)
* logic after group deletion must not check for enrichment of the deleted object ([63559bd](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/63559bd257dd1a90e19ecb82cb79c061a5a34fc8)), closes [univention/dev/internal/dev-issues/dev-incidents#155](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/155)
* use fixture for creating test groups ([9387ebe](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/9387ebe5e4c482d1e09e8f35817bda44376b2444)), closes [univention/dev/internal/dev-issues/dev-incidents#155](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/155)


### Reverts

* "ci: enable pre-commit" ([1b9aae8](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/1b9aae80c090aa33c7cb35ff4e16d9206fbcdb03))
* "fix: lint issues" ([8d9012b](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/8d9012b166d87f90e3d6feb14d46384a3940141e))

## [0.27.8](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.7...v0.27.8) (2025-09-02)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.2-build.20250821 ([f74ac3a](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/f74ac3afa50e49e54959c656232a8aa245d808dd)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)
* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.2-build.20250828 ([e1bd992](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/e1bd992cb1d0014b5de8d511a7d12194f909251e)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)
* lint issues ([5daaa71](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/5daaa7133ae276193df0bc8e58bb98ac4ab89957)), closes [univention/dev/internal/team-nubus#1368](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1368)

## [0.27.7](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.6...v0.27.7) (2025-08-21)


### Bug Fixes

* **standalone:** Correctly handle non OX-objects and add them to an own database ([1b9d2e3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/1b9d2e3fc67787385465dd79935d5089d811f682)), closes [univention/dev/internal/team-nubus#1366](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1366)
* **standalone:** Improve test_cache.py based on MR feedback ([d2d6d5c](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/d2d6d5cb1e077fefa222ea9df69a76e17d6a8b8d)), closes [univention/dev/internal/team-nubus#1366](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1366)
* **standalone:** Search for user in OX in case it is not in the cache ([e498625](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/e4986259563a71f46c822fabd8c0b198ef2bd14c)), closes [univention/dev/internal/team-nubus#1366](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1366)

## [0.27.6](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.5...v0.27.6) (2025-08-19)


### Bug Fixes

* case sensitive DNs in k8s ([9852396](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/985239685eaa8371af36b997d5b12ada60e04118)), closes [univention/dev/internal/team-nubus#1381](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1381)

## [0.27.5](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.4...v0.27.5) (2025-08-19)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base Docker tag to v5.2.2-build.20250814 ([83462c0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/83462c0c696be91185785777a3c103c26fe55402)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.27.4](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.3...v0.27.4) (2025-08-19)


### Bug Fixes

* **deps:** Update dependency univention/dev/nubus-for-k8s/common-ci to v1.44.1 ([1fccaa3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/1fccaa34d36a4f7efe13f874b42064932457f53c)), closes [#0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/0)

## [0.27.3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.2...v0.27.3) (2025-08-08)


### Bug Fixes

* remove non-functional manager field ([da776d6](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/da776d6f4ec9272176874da18eff7a3f75b7b543)), closes [univention/dev/internal/team-nubus#1064](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1064)

## [0.27.2](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.1...v0.27.2) (2025-07-29)


### Reverts

* chore(helm): Update helm dependencies after the repo move ([23f84af](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/23f84afed77df1e5ab8261769de5824265d85246))

## [0.27.1](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.27.0...v0.27.1) (2025-07-23)


### Bug Fixes

* **standalone:** Commit the KV databases to the filesystem at the end of every provisioning message ([f57dbb9](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/f57dbb94d37c988f4bb23b7b7ef4777aff63610d)), closes [univention/dev/internal/dev-issues/dev-incidents#144](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/144)

## [0.27.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.26.0...v0.27.0) (2025-07-21)


### Features

* **udm-oxresources:** use UDMs locking functionaliy ([c8abed9](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/c8abed93504d85a40da613b213483f2ed6649f04))
* Use current latest changes for OX Connector for Nubus4K8s ([9e08e36](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/9e08e367b6e076a176fda93c07b1c67a25d3e34a)), closes [univention/dev/internal/dev-issues/dev-incidents#148](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/148)


### Bug Fixes

* New ldap dependency for sanitization in shared codebase ([0b53feb](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/0b53feb9f8272e4a6bc41080ae16bc14be1b3aef)), closes [univention/dev/internal/dev-issues/dev-incidents#148](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/148)
* **ox-extension:** Compatibility with stack-data data-loader checks for Object exists in message ([f7ed43e](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/f7ed43e20098b5c2b262daafd7ba3c589d166379)), closes [univention/dev/internal/dev-issues/dev-incidents#148](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/148)
* **ox-extension:** Ensure the oxDeputyPermissionGiventTo extended attribute is the same in UCS and N4K ([1a1aa6b](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/1a1aa6b98ea882b632db98f46ac2102024833e61)), closes [univention/dev/internal/dev-issues/dev-incidents#148](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/148)
* **ox-extension:** fix standalone exdended_attribute oxDeputyPermissionGiventTo default type ([0a7db17](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/0a7db17836a8f8b9cc19872ff80a28c3212fb1ac)), closes [univention/dev/internal/dev-issues/dev-incidents#148](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/148)

## [0.26.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.25.1...v0.26.0) (2025-07-17)


### Features

* update ucs-base to 5.2.2-build.20250714 ([d33576c](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/d33576cd47669d2e01491b518bc26101064e16d8)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)
* update wait-for-dependency to 0.35.0 ([618c849](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/618c849eea2698258da4db020d1679afd8182780)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.25.1](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.25.0...v0.25.1) (2025-06-26)


### Bug Fixes

* dependency name change from nubus-common to common ([acf3c9c](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/acf3c9c92da1ac59138ec26cddc4bb48f1ddcaf0))

## [0.25.0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.24.3...v0.25.0) (2025-06-24)


### Features

* **packaged-integration-ox:** Add changelog entry ([0c64198](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/0c64198ee39aed2a912a037d14c8914eac17a9b8)), closes [univention/dev/projects/open-xchange/connector#131](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/131)
* **packaged-integration-ox:** Note about RELEASE_NAME != Nubus release name ([20e864c](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/20e864c97c43705c4a855c12b7e86889a29df220)), closes [univention/dev/projects/open-xchange/connector#131](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/131)


### Bug Fixes

* **packaged-integration-ox:** Add --install to helm command ([cd01ae0](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/cd01ae02358df7ef0384e2c534352c7bfe71945b)), closes [univention/dev/projects/open-xchange/connector#131](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/131)
* **packaged-integration-ox:** Reference to version information ([38306d1](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/38306d1d8dfafbe7cbfc63e6e27e1802d35eee31)), closes [univention/dev/projects/open-xchange/connector#131](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/issues/131)

## [0.24.3](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/compare/v0.24.2...v0.24.3) (2025-06-21)


### Bug Fixes

* bump umc-base-image version ([96a0412](https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/commit/96a04120df81eda2b7521b9673b2195f3790fab9)), closes [univention/dev/internal/team-nubus#1263](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1263)

## [0.24.2](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.24.1...v0.24.2) (2025-06-10)


### Bug Fixes

* Issue univention/dev/ucs[#2250](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/2250): (Try to) use convertguest=True when creating users ([3483bde](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/3483bdeb34b01ae70b17d0cdf19ddc5b593616c5))
* Issue univention/dev/ucs[#2250](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/2250): typo ([f049f76](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/f049f76984ac6d8b9aad6b492c8bf09b1552a4cf))
* univention/dev/internal/dev-issues/dev-incidents[#145](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/145) - ensure uniqueness of contextid in oxmail/oxcontext ([58cbeac](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/58cbeaccbaa8ed7573d3246d6f15ed24df9e7c6e))
* univention/dev/internal/dev-issues/dev-incidents[#145](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/145) - tests ([5af9354](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/5af935458031e74588aee4465fe0646c22a80f3d))

## [0.24.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.24.0...v0.24.1) (2025-05-28)


### Bug Fixes

* fix partial revert by `feat: OX-Connector 2.3.0` ([0ccd245](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/0ccd245d82f1f1df1b9ae0646da2385cc325187d)), closes [univention/open-xchange/provisioning#109](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/109)
* retry after UserCopy if user cannot be found ([5886db9](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/5886db9dd7fec1c4597a841fe4b0e5197a00353a)), closes [univention/open-xchange/provisioning#109](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/109)

## [0.24.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.23.0...v0.24.0) (2025-05-26)


### Features

* **packaged-integration-ox:** Add installation of OX Consumer ([233ee80](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/233ee8052b36fa5532e14db66d5caecaf773ddc7)), closes [univention/dev/docs/nubus-docs#94](https://git.knut.univention.de/univention/dev/docs/nubus-docs/issues/94)

## [0.23.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.22.2...v0.23.0) (2025-05-22)


### Features

* **docs:** Add OX Connector app to bibliography ([b08bada](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/b08bada68ddaaac7e7aff8b90ac7b2517eb0953d)), closes [univention/dev/internal/team-nubus#912](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/912)
* **packaged-integration-ox:** Add operation manual ([5c81e15](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/5c81e15d902e5b15ad0695e7fb9a183056c72190)), closes [univention/dev/internal/team-nubus#912](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/912)
* **packaged-integration-ox:** Refer to OX Connector app for UCS appliance ([dd94d4c](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/dd94d4c4426797704fdeca318b7a6efbb620a0ff)), closes [univention/dev/internal/team-nubus#1041](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1041)
* **packaged-integration-ox:** Refer to OX documentation for configuration ([18370aa](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/18370aa4604ca937487c436478707a151df6269e)), closes [univention/dev/internal/team-nubus#912](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/912)

## [0.22.2](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.22.1...v0.22.2) (2025-05-19)


### Bug Fixes

* **ox-connector:** allow configuration of PVC's size and storage class settings ([c35b1d4](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/c35b1d4c303cf655000932202d04092aac39ef5d)), closes [univention/dev/internal/team-nubus#1144](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1144)

## [0.22.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.22.0...v0.22.1) (2025-05-19)


### Bug Fixes

* Move context admin check to prevent change ([e96a15e](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/e96a15eb16bb12042ec7adfe9daac8486b41f261)), closes [#51517](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/51517) [univention/open-xchange/provisioning#123](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/123)
* Print correct log message on context admin skip ([9261d47](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/9261d472c7efb62b234dda36eddcb36743d1b05c)), closes [#51517](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/51517) [univention/open-xchange/provisioning#123](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/123)

## [0.22.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.21.1...v0.22.0) (2025-05-11)


### Features

* move and upgrade ucs-base-image to 0.17.3-build-2025-05-11 ([4af59d9](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/4af59d96cb0cbf406def3a81db6e99908c8410a1))

## [0.21.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.21.0...v0.21.1) (2025-05-09)


### Bug Fixes

* move addlicense pre-commit hook ([edb518f](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/edb518f60e29a8e4f7d590138d4e3201aefa827a))
* update common-ci to main ([db693c6](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/db693c65737261c8a623992523d099d85f7f819f))
* update common-ci to v1.40.4 ([27a9538](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/27a95389fabae78870332c38f4b0ac0e979355d8))

## [0.21.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.20.0...v0.21.0) (2025-04-29)


### Features

* Bump ucs-base-image version ([9e35e01](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/9e35e017840555ebb6d740ac97de22816c2e8fd7)), closes [univention/dev/internal/team-nubus#1155](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1155)


### Bug Fixes

* final version of wait-for-dependency ([b261794](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/b2617943268d6b1e4adc45f784129c7116164052)), closes [univention/dev/internal/team-nubus#1155](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1155)

## [0.20.0](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.19.1...v0.20.0) (2025-04-22)


### Features

* **docs:** Add navigation header and footer to docs ([7bb7557](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/7bb75575321d5a1665e4a350bd170a3be2247dfd)), closes [#124](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/124)

## [0.19.1](https://git.knut.univention.de/univention/open-xchange/provisioning/compare/v0.19.0...v0.19.1) (2025-04-15)


### Bug Fixes

* Add configurable log level ([1ad1020](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/1ad10209ce8bdc157875e5b8342e0821bd8ed7fb))
* change DockerImage to oficial ([926c93e](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/926c93e16ba341c6c12d5ee9172ed70dc1a25fda)), closes [#58187](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/58187) [univention/open-xchange/provisioning#122](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/122)
* Revert changes oxContextSelect syntax and adjust test. ([4dbcf0f](https://git.knut.univention.de/univention/open-xchange/provisioning/commit/4dbcf0f393b9c3aa1f9ebb23167c730cbbac7521)), closes [#58187](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/58187) [univention/open-xchange/provisioning#122](https://git.knut.univention.de/univention/open-xchange/provisioning/issues/122)

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
