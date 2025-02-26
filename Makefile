install: build-docs
	cp -r docs/build/html kedro
	pip install .

clean:
	rm -rf build dist docs/build kedro/html pip-wheel-metadata
	find . -regex ".*/__pycache__" -exec rm -rf {} +
	find . -regex ".*\.egg-info" -exec rm -rf {} +

install-pip-setuptools:
	python -m pip install -U "pip>=18.0, <19.0" "setuptools>=38.0, <39.0" wheel

legal:
	python tools/license_and_headers.py

lint:
	pre-commit run -a --hook-stage manual

test:
	pytest tests

e2e-tests:
	behave

SPHINXPROJ = Kedro

build-docs:
	./docs/build-docs.sh

devserver: build-docs
	cd docs && npm install && npm start

package: clean install
	python setup.py sdist bdist_wheel

install-test-requirements:
	pip install -r test_requirements.txt

install-pre-commit: install-test-requirements
	pre-commit install --install-hooks

uninstall-pre-commit:
	pre-commit uninstall
	pre-commit uninstall --hook-type pre-push
