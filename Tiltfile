# -*- mode: Python -*-
# pylint: disable=invalid-name

"""
Tilt definition file for running OX-Connector-Standalone in an helm environment
"""

DEFAULT_REGISTRY_APPCENTER = (
    'gitregistry.knut.univention.de/univention/open-xchange/provisioning'
)
DEFAULT_IMAGE_NAME_APPENTER = 'ox-connector-appcenter'
DEFAULT_IMAGE_TAG_APPCENTER = '0.0.1-dev-tilt'

DEFAULT_REGISTRY_STANDLONE = (
    'registry.souvap-univention.de/souvap/tooling/images/ox-connector'
)
DEFAULT_IMAGE_NAME_STANDLONE = 'ox-connector-standalone'
DEFAULT_IMAGE_TAG_STANDLONE = '0.0.1-dev-tilt'

config.define_bool(  # noqa: F821; pylint: disable=undefined-variable
    "build-appcenter",
    args=False,
    usage="Whether building the appcenter image beforehand",
)

config.define_string(  # noqa: F821; pylint: disable=undefined-variable
    "appcenter-registry",
    args=False,
    usage="Docker registry path for the appcenter image",
)

config.define_string(  # noqa: F821; pylint: disable=undefined-variable
    "standalone-registry",
    args=False,
    usage="Docker registry path for the standalone image",
)

config.define_string(  # noqa: F821; pylint: disable=undefined-variable
    "appcenter-name", args=False, usage="Docker image name for appcenter"
)

config.define_string(  # noqa: F821; pylint: disable=undefined-variable
    "standalone-name", args=False, usage="Docker image name for standalone"
)

config.define_string(  # noqa: F821; pylint: disable=undefined-variable
    "appcenter-tag", args=False, usage="Docker image tag for appcenter"
)

config.define_string(  # noqa: F821; pylint: disable=undefined-variable
    "standalone-tag", args=False, usage="Docker image tag for standalone"
)

config.define_string(  # noqa: F821; pylint: disable=undefined-variable
    "target", args=False, usage="Docker build target"
)

cfg = config.parse()  # noqa: F821; pylint: disable=undefined-variable

build_appcenter = cfg.get('build-appcenter', False)

appcenter_registry = cfg.get("appcenter-registry", DEFAULT_REGISTRY_APPCENTER)
appcenter_name = cfg.get("appcenter-name", DEFAULT_IMAGE_NAME_APPENTER)
appcenter_tag = cfg.get("appcenter-tag", DEFAULT_IMAGE_TAG_APPCENTER)

standalone_registry = cfg.get(
    "standalone-registry", DEFAULT_REGISTRY_STANDLONE
)
standalone_name = cfg.get("standalone-name", DEFAULT_IMAGE_NAME_STANDLONE)
standalone_tag = cfg.get("standalone-tag", DEFAULT_IMAGE_TAG_STANDLONE)

target = cfg.get('target', 'final')

# Check if namespace has been set
namespace = k8s_namespace()  # noqa: F821; pylint: disable=undefined-variable
if namespace == 'default':
    exit(  # pylint: disable=consider-using-sys-exit
        "Please specify a namespace in you kubeconfig"
    )
print(
    'Using namespace {}'.format(  # pylint: disable=consider-using-f-string
        namespace
    )
)

# Value of `current-context` from your `~/.kube/config`
# E.g. `kubernetes-admin@cluster.local`
context = k8s_context()  # noqa: F821; pylint: disable=undefined-variable
print(
    'Using context {}'.format(  # pylint: disable=consider-using-f-string
        context
    )
)

# Define current context as not production
allow_k8s_contexts(context)  # noqa: F821; pylint: disable=undefined-variable

# Build Appcenter image
if build_appcenter:
    appcenter_image_path = (
        '{}/{}:{}'.format(  # pylint: disable=consider-using-f-string
            appcenter_registry, appcenter_name, appcenter_tag
        )
    )
    print(
        'Building image {}'.format(  # pylint: disable=consider-using-f-string
            appcenter_image_path
        )
    )
    docker_build(  # noqa: F821; pylint: disable=undefined-variable
        appcenter_image_path,
        '.',
        dockerfile='Dockerfile',
        build_args={'version': '0.0.1-dev-tilt'},
    )

# Build Standalone image
standalone_image_path = (
    '{}/{}:{}'.format(  # pylint: disable=consider-using-f-string
        standalone_registry, standalone_name, standalone_tag
    )
)
print(
    'Building image {}'.format(  # pylint: disable=consider-using-f-string
        standalone_image_path
    )
)
print(
    'Using target {}'.format(target)  # pylint: disable=consider-using-f-string
)
docker_build(  # noqa: F821; pylint: disable=undefined-variable
    standalone_image_path,
    '.',
    dockerfile='Dockerfile.standalone',
    build_args={'version': '0.0.1-dev-tilt'},
    pull=True,
    target=target,
)

# Delete old docker images created by tilt
docker_prune_settings(  # noqa: F821; pylint: disable=undefined-variable
    disable=False,
    max_age_mins=360,
    num_builds=0,
    interval_hrs=1,
    keep_recent=2,
)

# Update helm deployment with new image
k8s_yaml(  # noqa: F821; pylint: disable=undefined-variable
    helm(  # noqa: F821; pylint: disable=undefined-variable
        'helm/ox-connector',
        name='ox-connector',
        values='./helm/ox-connector/tilt_values.yaml.example',
    )
)

# End
