## APIDIOMS

Simple REST API for idioms in the english language.

API comes with 8508 idioms scraped from [wiktionary](https://en.wiktionary.org/wiki/Category:English_idioms) - see `data/idioms.csv` for data.

### Stack

- FastAPI
- SQLModel
- Pydantic
- SQLite
- BeautifulSoup
- Requests
- asyncio
- aiocsv

## Start

Create venv & install depencencies.

```console
$ python3 -m uvicorn api.app:app --reload
```

### Docs

Visit `http://localhost:8000/docs` for documentation.
