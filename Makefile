.PHONY: install test type lint coverage

install:
	pip install -r requirements.txt

test:
	pytest --doctest-modules --junitxml=reports/junit/test-results.xml --cov=src --cov-report=xml --cov-report=html

type:
	mypy src

lint:
	flake8 src tests

coverage:
	coverage run -m pytest
	coverage report
	coverage html

perf:
	PYTHONPATH=./src pytest -k test_generate_output_performance
