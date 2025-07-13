# Sample Scripts

## SQLAlchemy to Markdown

For **declarative mapping**, from the directory of this file run:
```commandline
export DMDOC_MD_FILEPATH="./data/output/markdown/sqlalchemy-declarative.md"
dmdoc generate -s "./data/source/sqlalchemy-declarative.yaml" -f "./data/format/markdown.yaml"
```

For **imperative mapping**, from the directory of this file run:
```commandline
export DMDOC_MD_FILEPATH="./data/output/markdown/sqlalchemy-imperative.md"
dmdoc generate -s "./data/source/sqlalchemy-imperative.yaml" -f "./data/format/markdown.yaml"
```

## Beanie to Markdown

From the directory of this file run:
```commandline
export DMDOC_MD_FILEPATH="./data/output/markdown/beanie.md"
dmdoc generate -s "./data/source/beanie.yaml" -f "./data/format/markdown.yaml"
```
