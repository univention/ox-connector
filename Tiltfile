# -*- mode: Python -*-

allow_k8s_contexts('CHANGE_ME')

# docker_build(
#     'gitregistry.knut.univention.de/univention/open-xchange/provisioning/ox-connector-appcenter:latest',
#     '.',
#     dockerfile='Dockerfile',
#     build_args={'version': '1.2.3'}
#    )

docker_build(
    'registry.souvap-univention.de/souvap/tooling/images/ox-connector/ox-connector-standalone:debug',
    '.',
    dockerfile='Dockerfile.standalone',
    build_args={'version': '1.2.3'},
    pull=True,
    target="final"
)

docker_prune_settings(
    disable=False,
    max_age_mins=360,
    num_builds=0,
    interval_hrs=1,
    keep_recent=2
)

k8s_yaml(
    helm(
        'helm/ox-connector',
        name='ox-connector',
        namespace='CHANGE_ME',
        values='../deploy-souvap-ng/helmfile/apps/provisioning/values-oxconnector.yaml'
    )
)
