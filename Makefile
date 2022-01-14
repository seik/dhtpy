check:
	poetry run isort .
	poetry run black .
	poetry run mypy .