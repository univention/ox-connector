# Remote Consumer - Development README

## Introduction

**Remote Consumer** is a CLI utility that manages the ox-connector consumer against remote deployments. It fetches required configurations (LDAP, OpenXchange, Provisioning API settings) from remote hosts and executes the consumer locally, avoiding SSH tunnels for the actual consumer process.

### Features

- **SSH Mode**: Fetch configurations from remote SSH hosts (10.207.237.37, etc.) and run consumer locally
- **Kubernetes Mode**: Placeholder for future Kubernetes deployment support
- **Local Execution**: Runs consumer locally using fetched environment variables (no SSH tunnel for consumer process)

### Options

The tool supports following subcommands:

1. **`configurations`**: Fetch and display JSON configurations from remote deployment
2. **`run`**: Fetch configurations and execute consumer locally
4. **`test`**: Run pytest tests locally using fetched configurations
5. **`udm`**: Run UDM REST client commands (for fixing/cleaning up when connector crashes)

To get a full list of all options look at the help
```bash
docker compose run --remove-orphans dev ssh --help
docker compose run --remove-orphans dev kubernetes --help
```

**Kubernetes Mode:**
The used kube config will be `~/.kube/config`, this can be changed by setting the environment variable `KUBE_CONFIG`.

```bash
KUBE_CONFIG="~/.kube/config_uv" docker compose run --remove-orphans dev kubernetes ...
```


## Commands

### `configurations` - Fetch and print configurations

Fetch required configurations from the remote deployment and print them as JSON.

**SSH Mode:**
```bash
docker compose run --remove-orphans dev ssh 10.207.237.37 configurations
```

**Kubernetes Mode:**
```bash
docker compose run --remove-orphans dev kubernetes jburgmeier-ox configurations
```

### `run` - Run consumer locally

Fetch configurations from the remote deployment and run the consumer locally using those settings.

**SSH Mode:**
```bash
docker compose run --remove-orphans dev ssh 10.207.237.37 run
```

**Kubernetes Mode:**
```bash
docker compose run --remove-orphans dev kubernetes jburgmeier-ox run
```

### `udm` - Run udm command

Run UDM commands on the deployment, might be helpfull if tests/consumer crashes and some data stays behind.

**SSH Mode:**
```bash
docker compose run --remove-orphans dev ssh 10.207.237.37 udm users/user remove --dn="uid=user111,cn=users,dc=ucs,dc=test"
docker compose run --remove-orphans dev ssh 10.207.237.37 udm oxmail/accessprofile remove --dn="cn=accessprofile_usm,cn=accessprofiles,cn=open-xchange,dc=ucs,dc=test"
```

**Kubernetes Mode:**
```bash
docker compose run --remove-orphans dev kubernetes jburgmeier-ox udm users/user remove --dn="uid=user111,cn=users,dc=ucs,dc=test"
docker compose run --remove-orphans dev kubernetes jburgmeier-ox udm oxmail/accessprofile remove --dn="cn=accessprofile_usm,cn=accessprofiles,cn=open-xchange,dc=ucs,dc=test"
```

## Usage examples

### SSH

#### Prerequistes

UCS deployment with OX and provisioning

1. Create environment in jenkins `https://jenkins2022.knut.univention.de/job/UCS-5.2/job/UCS-5.2-4/view/Personal%20environments/job/UcsOxConnectorEnvironment/`
2. Install provisioning `univention-app install provisioning-service`

#### Run

Run consumer and tests, the tests must run in the same container because they share some state like the ox credentials file.

```bash
docker compose run --remove-orphans dev ssh 10.207.248.11 run
docker compose run --remove-orphans dev ssh 10.207.248.11 test -s -v
```

### Kubernetes

#### Prerequistes

See README.standalone.md how to setup the environment

#### Run

Run consumer and tests, the tests must run in the same container because they share some state like the ox credentials file.

```bash
docker compose run --remove-orphans dev kubernetes jburgmeier-ox run
docker compose run --remove-orphans dev kubernetes jburgmeier-ox test -s -v
```
