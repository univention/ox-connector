# ox-connector

![Version: 0.2.0](https://img.shields.io/badge/Version-0.2.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.0](https://img.shields.io/badge/AppVersion-1.0.0-informational?style=flat-square)

A Helm chart for the ox-connector

**Homepage:** <https://www.univention.de/>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus/charts | nubus-common | 0.24.2 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| environment | object | `{}` |  |
| extraVolumeMounts | list | `[]` | Optionally specify an extra list of additional volumeMounts. |
| extraVolumes | list | `[]` | Optionally specify an extra list of additional volumes. |
| fullnameOverride | string | `""` |  |
| global.imagePullPolicy | string | `nil` | Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally. "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails. |
| global.imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| global.imageRegistry | string | `"artifacts.software-univention.de"` | Container registry address. |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| oxConnector.domainName | string | `nil` | OX-Mail-Domain to generate OX-email-addresses |
| oxConnector.image.pullPolicy | string | `nil` |  |
| oxConnector.image.registry | string | `nil` |  |
| oxConnector.image.repository | string | `"nubus-dev/images/ox-connector-standalone"` |  |
| oxConnector.image.tag | string | `"latest"` |  |
| oxConnector.logLevel | string | `"INFO"` | OX Connector log level Chose from "DEBUG", "INFO", "WARNING" and "ERROR". |
| oxConnector.oxDefaultContext | string | `"10"` | Default context for users (has to exist) |
| oxConnector.oxImapServer | string | `nil` | Default IMAP server for new users (if not set explicitely there) |
| oxConnector.oxLanguage | string | `"de_DE"` | Default language for new users |
| oxConnector.oxLocalTimezone | string | `"Europe/Berlin"` | Default timezone for new users |
| oxConnector.oxMasterAdmin | string | `"oxadminmaster"` | OX Admin username (the OX Admin can create, modify, delete contexts; has to exist) |
| oxConnector.oxMasterPassword | string | `nil` | OX Admin password |
| oxConnector.oxSmtpServer | string | `nil` | Default SMTP server for new users (if not set explicitely there) |
| oxConnector.oxSoapServer | string | `nil` | The server where Open-Xchange is installed |
| persistence.size | string | `"1Gi"` | Specify PVCs size |
| persistence.storageClass | string | `""` | Specify storageClassName - Leave empty to use the default storage class |
| podAnnotations | object | `{}` |  |
| podSecurityContext.fsGroup | int | `1000` |  |
| podSecurityContext.runAsGroup | int | `1000` |  |
| podSecurityContext.runAsNonRoot | bool | `true` |  |
| podSecurityContext.runAsUser | int | `1000` |  |
| podSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| probes.liveness.exec.command[0] | string | `"/bin/sh"` |  |
| probes.liveness.exec.command[1] | string | `"-c"` |  |
| probes.liveness.exec.command[2] | string | `"exit 0\n"` |  |
| probes.liveness.failureThreshold | int | `3` |  |
| probes.liveness.initialDelaySeconds | int | `120` |  |
| probes.liveness.periodSeconds | int | `30` |  |
| probes.liveness.successThreshold | int | `1` |  |
| probes.liveness.timeoutSeconds | int | `3` |  |
| probes.readiness.exec.command[0] | string | `"/bin/sh"` |  |
| probes.readiness.exec.command[1] | string | `"-c"` |  |
| probes.readiness.exec.command[2] | string | `"exit 0\n"` |  |
| probes.readiness.failureThreshold | int | `30` |  |
| probes.readiness.initialDelaySeconds | int | `30` |  |
| probes.readiness.periodSeconds | int | `15` |  |
| probes.readiness.successThreshold | int | `1` |  |
| probes.readiness.timeoutSeconds | int | `3` |  |
| provisioningApi.auth | object | `{"password":"","username":"ox-connector"}` | Authentication parameters |
| provisioningApi.auth.password | string | `""` | The password to authenticate with. |
| provisioningApi.auth.username | string | `"ox-connector"` | The username to authenticate with. |
| provisioningApi.config.maxAcknowledgementRetries | int | `3` | The maximum number of retries for acknowledging a message |
| provisioningApi.connection | object | `{"baseUrl":""}` | Connection parameters |
| provisioningApi.connection.baseUrl | string | `""` | The base URL the provisioning API is reachable at. (e.g. "https://provisioning-api") |
| replicaCount | int | `1` |  |
| resources.limits.cpu | string | `"4"` |  |
| resources.limits.memory | string | `"4Gi"` |  |
| resources.requests.cpu | string | `"250m"` |  |
| resources.requests.memory | string | `"512Mi"` |  |
| resourcesWaitForDependency | object | `{}` | Deployment resources for the dependency waiters |
| securityContext.allowPrivilegeEscalation | bool | `false` |  |
| securityContext.capabilities.drop[0] | string | `"ALL"` |  |
| securityContext.privileged | bool | `false` |  |
| securityContext.readOnlyRootFilesystem | bool | `true` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automountServiceAccountToken | bool | `false` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.labels | object | `{}` | Additional custom labels for the ServiceAccount. |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |
| waitForDependency.image.pullPolicy | string | `nil` |  |
| waitForDependency.image.registry | string | `nil` |  |
| waitForDependency.image.repository | string | `"nubus/images/wait-for-dependency"` |  |
| waitForDependency.image.tag | string | `"0.35.0@sha256:61dfaea28a2b150459138dfd6a554ce53850cee05ef2a72ab47bbe23f2a92d0d"` |  |
