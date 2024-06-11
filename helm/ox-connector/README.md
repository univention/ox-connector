# ox-connector

![Version: 0.2.0](https://img.shields.io/badge/Version-0.2.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.0](https://img.shields.io/badge/AppVersion-1.0.0-informational?style=flat-square)

A Helm chart for the ox-connector

**Homepage:** <https://www.univention.de/>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/common-helm/helm | common | ^0.1.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| environment | object | `{}` |  |
| extraVolumeMounts | list | `[]` | Optionally specify an extra list of additional volumeMounts. |
| extraVolumes | list | `[]` | Optionally specify an extra list of additional volumes. |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"Always"` |  |
| image.registry | string | `"artifacts.software-univention.de"` |  |
| image.repository | string | `"nubus-dev/images/ox-connector-standalone"` |  |
| image.sha256 | string | `nil` | Define image sha256 as an alternative to `tag` |
| image.tag | string | `"latest"` |  |
| image.waitForDependency.imagePullPolicy | string | `"IfNotPresent"` |  |
| image.waitForDependency.registry | string | `"artifacts.software-univention.de"` |  |
| image.waitForDependency.repository | string | `"nubus/images/wait-for-dependency"` |  |
| image.waitForDependency.tag | string | `"0.25.0@sha256:71a4d66fd67db6f92212b1936862b2b0d5a678d412213d74452a9195c2fe67f7"` |  |
| ingress | object | `{"enabled":false}` | Kubernetes ingress |
| ingress.enabled | bool | `false` | Set this to `true` in order to enable the installation on Ingress related objects. |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| oxConnector.domainName | string | `nil` | OX-Mail-Domain to generate OX-email-addresses |
| oxConnector.logLevel | string | `"INFO"` | OX Connector log level Chose from "DEBUG", "INFO", "WARNING" and "ERROR". |
| oxConnector.oxDefaultContext | string | `"10"` | Default context for users (has to exist) |
| oxConnector.oxImapServer | string | `nil` | Default IMAP server for new users (if not set explicitely there) |
| oxConnector.oxLanguage | string | `"de_DE"` | Default language for new users |
| oxConnector.oxLocalTimezone | string | `"Europe/Berlin"` | Default timezone for new users |
| oxConnector.oxMasterAdmin | string | `"oxadminmaster"` | OX Admin username (the OX Admin can create, modify, delete contexts; has to exist) |
| oxConnector.oxMasterPassword | string | `nil` | OX Admin password |
| oxConnector.oxSmtpServer | string | `nil` | Default SMTP server for new users (if not set explicitely there) |
| oxConnector.oxSoapServer | string | `nil` | The server where Open-Xchange is installed |
| podAnnotations | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| probes.liveness.enabled | bool | `true` |  |
| probes.liveness.failureThreshold | int | `3` |  |
| probes.liveness.initialDelaySeconds | int | `120` |  |
| probes.liveness.periodSeconds | int | `30` |  |
| probes.liveness.successThreshold | int | `1` |  |
| probes.liveness.timeoutSeconds | int | `3` |  |
| probes.readiness.enabled | bool | `true` |  |
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
| securityContext | object | `{}` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |
