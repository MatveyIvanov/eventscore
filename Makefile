test:
	poetry run pytest .
unittest:
	poetry run pytest . -m unit
integrationtest:
	poetry run pytest . -m integration
e2etest:
	poetry run pytest . -m e2e
lint:
	poetry run flake8 .
	poetry run ruff check
analyze:
	poetry run mypy .
	poetry run pyright .
format:
	poetry run black $(OPTS) .
	poetry run ruff format $(OPTS)
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
update-examples:
	cp -r eventscore examples/django/src/
	cp -r eventscore examples/fastapi/src/

django-example:
	$(MAKE) update-examples
	docker compose -f examples/django/docker/docker-compose.yml up $(OPTS)

fastapi-example:
	$(MAKE) update-examples
	docker compose -f examples/fastapi/docker/docker-compose.yml up $(OPTS)

