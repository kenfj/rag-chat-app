# note: use -s to print stdout
poetry run pytest --cov=src --cov-report=html --cov-report=term ./tests

# open htmlcov/index.html
