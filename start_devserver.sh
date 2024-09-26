export REQUESTS_CA_BUNDLE=~/.aspnet/https/certificate.pem
poetry run fastapi dev src/main.py

# http://127.0.0.1:8000/docs
# http://127.0.0.1:8000/static/index.html
