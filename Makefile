test:
	poetry run pytest .
unittest:
	poetry run pytest . -m unit
integrationtest:
	poetry run pytest . -m integration
lint:
	poetry run flake8 .
typecheck:
	poetry run mypy .
format:
	poetry run black $(OPTS) .
formatcheck:
	$(MAKE) OPTS=--check format
sort:
	poetry run isort --profile black --filter-files $(OPTS) .
sortcheck:
	$(MAKE) OPTS=--check sort
install-git-hooks:
	poetry run pre-commit install --hook-type pre-commit
uninstall-git-hooks:
	poetry run pre-commit uninstall -t pre-commit
docsbuild:
	cd docs \
		&& sphinx-apidoc -f -o ../docs/source/ ../eventscore \
		&& $(MAKE) html
