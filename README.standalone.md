### Standalone development

1. Build the AppCenter image by running `build_docker_image` script.
2. Run the steps on `README.md` on the [listener-container-base](https://git.knut.univention.de/univention/customers/dataport/upx/container-listener-base) and ensure `ssl`, `secret` and `docker-compose.override.yaml` have been created.
3. Configure additional domains if needed under the `docker-compose.override.yaml` to ensure doveadm HTTP API is reachable from within the container.
4. Use the `docker-compose.yaml` file to bring up the environment.
5. Happy development!

