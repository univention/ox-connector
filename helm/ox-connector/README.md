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
| affinity | object | `{}` | Pod affinity rules for the OX Connector workload. |
| environment | object | `{}` | Additional environment variables for deployment templates. |
| extraVolumeMounts | list | `[]` | Optionally specify an extra list of additional volumeMounts. |
| extraVolumes | list | `[]` | Optionally specify an extra list of additional volumes. |
| fullnameOverride | string | `""` | Override the fully qualified chart name. |
| global.imagePullPolicy | string | `nil` | Image pull policy for all container images that don't define their own pull policy. For details, see https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy. |
| global.imagePullSecrets | list | `[]` | Credentials to fetch images from a private registry. For details, see https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/. |
| global.imageRegistry | string | `"artifacts.software-univention.de"` | Container registry address. |
| nameOverride | string | `""` | Override the chart name. |
| nodeSelector | object | `{}` | Node selector for scheduling the OX Connector pod. |
| openXchange.auth.existingSecret.keyMapping.password | string | `nil` | Key in the existing Secret that contains the OX Admin password. Set this value to use a key with a different name. |
| openXchange.auth.existingSecret.name | string | `nil` | Name of an existing Secret that contains the OX Admin password. The value in "openXchange.auth.password" is ignored if this value is set. |
| openXchange.auth.password | string | `nil` | Password of the OX Admin user. |
| openXchange.auth.username | string | `"oxadminmaster"` | Username of the OX Admin user. The OX Admin user can create, modify, and delete contexts and must already exist. |
| openXchange.domainName | string | `nil` | OX mail domain that the connector uses to generate email addresses. |
| openXchange.logLevel | string | `"INFO"` | OX Connector log level. Choose from "DEBUG", "INFO", "WARNING", and "ERROR". |
| openXchange.mappings.groupIdentifier | string | `"name"` | UDM group property that the connector uses as the unique group identifier in OX. |
| openXchange.mappings.sharedAccountIdentifier | string | `"name"` | UDM shared account property that the connector uses as the unique shared account identifier in OX. |
| openXchange.mappings.userIdentifier | string | `"username"` | UDM user property that the connector uses as the unique user identifier in OX. |
| openXchange.oxDbConnectionString | string | `nil` | SQLAlchemy DB connection URL for the OX connector. |
| openXchange.oxDefaultContext | string | `"10"` | Default OX context for users. The context must already exist. |
| openXchange.oxDeputyPermissions | bool | `false` | Enable provisioning of OX deputy permissions. |
| openXchange.oxImapServer | string | `nil` | Default IMAP server for new users if no IMAP server is set on the user object. |
| openXchange.oxLanguage | string | `"de_DE"` | Default language for new users. |
| openXchange.oxLocalTimezone | string | `"Europe/Berlin"` | Default time zone for new users. |
| openXchange.oxSharedAccount | bool | `true` | Enable provisioning of OX shared accounts. |
| openXchange.oxSmtpServer | string | `nil` | Default SMTP server for new users if no SMTP server is set on the user object. |
| openXchange.oxSoapServer | string | `nil` | Server where OX App Suite is installed. |
| oxConnector.extraEnvVars | list | `[]` | Array with extra environment variables to add to containers. |
| oxConnector.image.pullPolicy | string | `nil` | Image pull policy for the OX Connector container image. |
| oxConnector.image.registry | string | `nil` | Container registry for the OX Connector image. |
| oxConnector.image.repository | string | `"nubus-dev/images/ox-connector-standalone"` | Repository of the OX Connector image. |
| oxConnector.image.tag | string | `"latest"` | Tag of the OX Connector image. |
| persistence.size | string | `"1Gi"` | Persistent volume claim size. |
| persistence.storageClass | string | `""` | Storage class name. Leave empty to use the default storage class. |
| podAnnotations | object | `{}` | Additional annotations for the OX Connector pod. |
| podSecurityContext.fsGroup | int | `1000` | File system group ID for mounted volumes. |
| podSecurityContext.runAsGroup | int | `1000` | Group ID for the OX Connector pod. |
| podSecurityContext.runAsNonRoot | bool | `true` | Require the OX Connector pod to run as a non-root user. |
| podSecurityContext.runAsUser | int | `1000` | User ID for the OX Connector pod. |
| podSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` | Seccomp profile type for the OX Connector pod. |
| probes.liveness.exec.command | list | `["/bin/sh","-c","exit 0\n"]` | Command for the liveness probe. |
| probes.liveness.failureThreshold | int | `3` | Number of failed liveness probes before Kubernetes restarts the container. |
| probes.liveness.initialDelaySeconds | int | `120` | Initial delay in seconds before the liveness probe starts. |
| probes.liveness.periodSeconds | int | `30` | Interval in seconds between liveness probe executions. |
| probes.liveness.successThreshold | int | `1` | Number of successful liveness probes required to mark the container healthy. |
| probes.liveness.timeoutSeconds | int | `3` | Timeout in seconds for the liveness probe. |
| probes.readiness.exec.command | list | `["/bin/sh","-c","exit 0\n"]` | Command for the readiness probe. |
| probes.readiness.failureThreshold | int | `30` | Number of failed readiness probes before Kubernetes marks the container not ready. |
| probes.readiness.initialDelaySeconds | int | `30` | Initial delay in seconds before the readiness probe starts. |
| probes.readiness.periodSeconds | int | `15` | Interval in seconds between readiness probe executions. |
| probes.readiness.successThreshold | int | `1` | Number of successful readiness probes required to mark the container ready. |
| probes.readiness.timeoutSeconds | int | `3` | Timeout in seconds for the readiness probe. |
| provisioningApi.auth | object | `{"existingSecret":{"keyMapping":{"password":null},"name":null},"password":null,"username":"ox-consumer"}` | Authentication parameters for the Provisioning API subscription user. |
| provisioningApi.auth.existingSecret.keyMapping.password | string | `nil` | Key in the existing Secret that contains the password. Set this value to use a key with a different name. |
| provisioningApi.auth.existingSecret.name | string | `nil` | Name of an existing Secret that contains the Provisioning API password. The value in "provisioningApi.auth.password" is ignored if this value is set. |
| provisioningApi.auth.password | string | `nil` | Password for authenticating to the Provisioning API. |
| provisioningApi.auth.username | string | `"ox-consumer"` | Username for authenticating to the Provisioning API. |
| provisioningApi.config.maxAcknowledgementRetries | int | `3` | Maximum number of retries for acknowledging a message. |
| provisioningApi.connection | object | `{"baseUrl":""}` | Connection parameters for the Provisioning API. |
| provisioningApi.connection.baseUrl | string | `""` | Base URL where the Provisioning API is reachable, for example "https://provisioning-api". |
| provisioningApi.resync.auth.existingSecret.keyMapping.password | string | `nil` | Key in the existing Secret that contains the admin password. Set this value to use a key with a different name. |
| provisioningApi.resync.auth.existingSecret.name | string | `nil` | Name of an existing Secret that contains the Provisioning API admin password. The value in "provisioningApi.resync.auth.password" is ignored if this value is set. |
| provisioningApi.resync.auth.password | string | `nil` | Admin password for authenticating to the Provisioning API during resync. |
| provisioningApi.resync.auth.username | string | `"admin"` | Admin username for authenticating to the Provisioning API during resync. |
| provisioningApi.resync.enabled | bool | `true` | Enable database resync on the first startup if the database is empty. |
| replicaCount | int | `1` | Number of OX Connector replicas. |
| resources.limits.cpu | string | `"4"` | CPU limit for the OX Connector container. |
| resources.limits.memory | string | `"4Gi"` | Memory limit for the OX Connector container. |
| resources.requests.cpu | string | `"250m"` | Requested CPU for the OX Connector container. |
| resources.requests.memory | string | `"512Mi"` | Requested memory for the OX Connector container. |
| resourcesWaitForDependency | object | `{"limits":{"cpu":"200m","memory":"128Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}` | Deployment resources for the dependency waiters |
| resourcesWaitForDependency.limits.cpu | string | `"200m"` | CPU limit for dependency waiter containers. |
| resourcesWaitForDependency.limits.memory | string | `"128Mi"` | Memory limit for dependency waiter containers. |
| resourcesWaitForDependency.requests.cpu | string | `"100m"` | Requested CPU for dependency waiter containers. |
| resourcesWaitForDependency.requests.memory | string | `"64Mi"` | Requested memory for dependency waiter containers. |
| securityContext.allowPrivilegeEscalation | bool | `false` | Allow privilege escalation in the OX Connector container. |
| securityContext.capabilities.drop | list | `["ALL"]` | Linux capabilities to drop from the OX Connector container. |
| securityContext.privileged | bool | `false` | Run the OX Connector container in privileged mode. |
| securityContext.readOnlyRootFilesystem | bool | `true` | Mount the OX Connector container root filesystem as read-only. |
| securityContext.runAsGroup | int | `1000` | Group ID for the OX Connector container. |
| securityContext.runAsNonRoot | bool | `true` | Require the OX Connector container to run as a non-root user. |
| securityContext.runAsUser | int | `1000` | User ID for the OX Connector container. |
| securityContext.seccompProfile.type | string | `"RuntimeDefault"` | Seccomp profile type for the OX Connector container. |
| serviceAccount.annotations | object | `{}` | Additional annotations for the service account. |
| serviceAccount.automountServiceAccountToken | bool | `false` | Allow automatic mounting of the service account token. |
| serviceAccount.create | bool | `true` | Create a service account for the OX Connector. |
| serviceAccount.labels | object | `{}` | Additional custom labels for the ServiceAccount. |
| serviceAccount.name | string | `""` | Service account name. If this value is empty and "serviceAccount.create" is true, the chart generates a name from the fullname template. |
| tolerations | list | `[]` | Tolerations for scheduling the OX Connector pod. |
| waitForDependency.image.pullPolicy | string | `nil` | Image pull policy for the dependency waiter image. |
| waitForDependency.image.registry | string | `nil` | Container registry for the dependency waiter image. |
| waitForDependency.image.repository | string | `"nubus/images/wait-for-dependency"` | Repository of the dependency waiter image. |
| waitForDependency.image.tag | string | `"0.36.12@sha256:7150d72c8f342a05b945ce1b21464864aa91590d00f65ebe4b628571cce34efc"` | Tag of the dependency waiter image. |
