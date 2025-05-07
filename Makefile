MAKE_DIR := $(shell pwd)

test:
	$(MAKE) test-unit
	$(MAKE) test-integration
	$(MAKE) test-e2e
test-unit:
	poetry run pytest . -m unit
test-integration:
	$(MAKE) compose-up DIR="tests/integration/redis" OPTS="--build"
	poetry run pytest . -m integration $(OPTS) || true
	$(MAKE) compose-down DIR="tests/integration/redis"
test-e2e:
	$(MAKE) compose-up DIR="tests/e2e/django/docker" OPTS="--build"
	poetry run pytest . -m e2e $(OPTS) || true
	$(MAKE) compose-down DIR="tests/e2e/django/docker"
compose-up:
	cd $(DIR) && (docker-compose up -d $(OPTS) || docker compose up -d $(OPTS))
compose-down:
	cd $(DIR) && (docker-compose down -f || docker compose down)
lint:
	poetry run flake8 .
	poetry run ruff check
analyze:
	poetry run mypy .
	poetry run pyright .
format:
	poetry run black $(OPTS) .
	# poetry run ruff format $(OPTS)
formatcheck:
	$(MAKE) OPTS=--check format
sort:
	poetry run isort --profile black --filter-files $(OPTS) .
sortcheck:
	$(MAKE) OPTS=--check sort
tox:
	poetry run tox
install-git-hooks:
	poetry run pre-commit install --hook-type pre-commit
uninstall-git-hooks:
	poetry run pre-commit uninstall -t pre-commit
docs:
	cd docs \
		&& poetry run sphinx-apidoc -f -o ../docs/source/ ../eventscore \
		&& poetry run $(MAKE) html
update-examples-n-tests:
	cp -r eventscore examples/django/src/
	cp -r eventscore examples/fastapi/src/
	cp -r eventscore tests/e2e/django/src/
django-example:
	$(MAKE) update-examples-n-tests
	cd examples/django/docker && (docker-compose up $(OPTS) || docker compose up $(OPTS))
fastapi-example:
	$(MAKE) update-examples-n-tests
	cd examples/fastapi/docker && (docker-compose up $(OPTS) || docker compose up $(OPTS))
