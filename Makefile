install:
	pip install --upgrade .

test:
	python -m pytest --cov mmd
