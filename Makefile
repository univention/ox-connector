.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

PY_MODULES := tests univention-ox-provisioning
PY_PATHS := $(PY_MODULES)
PY_FILES := $(shell find $(PY_PATHS) -name '*.py') app/listener_trigger

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr univention-ox-provisioning/build/
	rm -fr univention-ox-provisioning/dist/
	rm -fr univention-ox-provisioning/.eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

format: ## format source code
	isort --apply --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --thirdparty pytest --project udm_rest --project udm_rest_client --project univention --skip univention-ox-provisioning/setup.py $(PY_PATHS) app/listener_trigger
	black --target-version py38 $(PY_PATHS) app/listener_trigger

lint-isort:
	isort --check-only --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --thirdparty pytest --project udm_rest --project udm_rest_client --project univention --skip univention-ox-provisioning/setup.py $(PY_PATHS) app/listener_trigger

lint-black:
	black --check --target-version py38 $(PY_PATHS) app/listener_trigger

lint-flake8:
	flake8 --max-line-length=105 --ignore=W503 $(PY_PATHS) app/listener_trigger

lint-coverage: .coverage
	coverage report --show-missing --fail-under=33

lint: lint-isort lint-black lint-flake8 ## check source code style

test: ## run tests (with the current active Python interpreter)
	python3 -m pytest -l -v -c univention-ox-provisioning/setup.cfg tests

.coverage: $(PY_FILES)
	coverage run --source tests,ucsschool -m pytest tests

coverage: .coverage ## check code coverage with the current Python interpreter
	coverage report --show-missing $(MY_COVERAGE_REPORT_ARGS)

coverage-html: coverage ## check code coverage, create HTML report and show in browser
	coverage html
	$(BROWSER) htmlcov/index.html

install: clean ## install the package to the active Python's site-packages
	pip3 install -e appsuite/univention-ox
	pip3 install -e appsuite/univention-ox-soap-api
	pip3 install -e univention-ox-provisioning

install-linting:  ## install linting packages to the active Python's site-packages
	pip3 install --compile black flake8 isort pytest pytest-asyncio

build-docker-image: clean ## build docker image
	./build_docker_image
