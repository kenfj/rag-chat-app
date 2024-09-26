# RAG Chat App Basic Example

Basic RAG chat sample app with ChatGPT style.

## Tech Stacks

* All works locally
  - Ollama llama3.1 for local LLM
  - Azure AI Search Emulator for local search
* LiteLLM as a adaptor for various LLM
* minimal sample code
  - backend is Python FastAPI
  - frontend is plain html (instead of React stuff)

## Quick Start

* start AzureSearchEmulator (see setup below)

```bash
cd AzureSearchEmulator

docker compose up -d
docker compose logs -f
```

* start dev server

```bash
poetry install

./start_devserver.sh
```

* http://127.0.0.1:8000/static/index.html
* http://127.0.0.1:8000/docs

* open with VSCode

```bash
poetry shell
export REQUESTS_CA_BUNDLE=~/.aspnet/https/certificate.pem
code .
```

## Setup Notes

* FastAPI: https://github.com/fastapi/fastapi

```bash
pyenv local 3.12.5

poetry init -n

poetry add -G dev ipykernel
poetry add fastapi[standard] litellm azure-search-documents python-dotenv
```

* Ollama: https://github.com/ollama/ollama
  - used with LiteLLM-Ollama: https://docs.litellm.ai/docs/providers/ollama

```bash
brew install ollama

ollama run llama3.1  # or phi3 or something you prefer
# >>> Hello!
# Hello there! How can I help you today?
# >>> /bye
```

* drawdown.js: markdown to html converter
  - https://github.com/adamvleggett/drawdown

```bash
curl -OL https://raw.githubusercontent.com/adamvleggett/drawdown/refs/heads/master/drawdown.js
```

## Azure Search Emulator

* Azure Search Emulator: https://github.com/feature23/AzureSearchEmulator
* dotnet-sdk: https://formulae.brew.sh/cask/dotnet-sdk
* setup local https: https://qiita.com/j_kitayama_hoge000/items/26cd7a5ef0b2fac53fce

```bash
dotnet dev-certs https --check

# maybe you will need this
dotnet dev-certs https --trust

# create new certs (path can be different)
dotnet dev-certs https -ep ~/.aspnet/https/aspnetapp.pfx -p password
```

* clone AzureSearchEmulator and edit `docker-compose.yml`
  - update `ASPNETCORE_Kestrel__Certificates__Default__Path` and `volumes`

```yaml
services:
  web:
    build: .
    ports:
      - 5080:80
      - 5081:443
    environment:
      - ASPNETCORE_URLS=https://+;http://+
      - ASPNETCORE_HTTPS_PORT=5081
      - ASPNETCORE_Kestrel__Certificates__Default__Password=password
      - ASPNETCORE_Kestrel__Certificates__Default__Path=/https/aspnetapp.pfx
    volumes:
      - indexes:/app/indexes
      - ~/.aspnet/https:/https:ro
volumes:
  indexes:
```

* start server and try from curl

```bash
docker compose up -d

# you should see some json from curl output
curl https://localhost:5081/
```

* convert pfx to pem for Python (MacOS user)

```bash
cd ~/.aspnet/https

openssl pkcs12 -in aspnetapp.pfx -out certificate.pem -nodes

# Python requires this environment variable
export REQUESTS_CA_BUNDLE=~/.aspnet/https/certificate.pem
```

* you may want to try from Postman or Insomnia for debug in case of trouble
* (another option?): https://github.com/tomasloksa/azure-search-emulator

## Add index and documents from Python notebook

* Note: collection/ComplexField are not implemented in AzureSearchEmulator
* make sure to install Jupyter extension in your VSCode
* open and run with VSCode [src/notes/azure-ai-search-notes.py](src/notes/azure-ai-search-notes.py)

## UI libs

(Optional) popular Python GUI

* https://streamlit.io/
* https://www.gradio.app/
* https://docs.chainlit.io/get-started/overview
