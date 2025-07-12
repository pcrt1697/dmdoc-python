# dmdoc-python
A Python package for data model documentation generator.

**Why:** keeping data model documentation up to date is boring.

**How:** a utility that produces the documentation directly from the code by:
* scanning data models from Python ORM/ODM libraries;
* producing the documentation in various formats.

Doing this way, developers only need to write entity and field descriptions in the source code and
`dmdoc` takes care of everything else (e.g. data types, keys, relationships, ...).  

Main features:
* A CLI to produce data model documentation;
* Pluggable sources, sinks and data types.

### Table of Content
* [Overview](#overview)
* [Usage](#usage)
  * [Installation](#installation)
  * [CLI](#cli)
  * [Extending dmdoc](#extending-dmdoc)
* [Sources](#sources)
  * [Beanie](#beanie)
  * [SQLAlchemy](#sqlalchemy)
* [Formatters](#formatters)
  * [Markdown](#markdown)
* [Data types](#data-types)
* [Coming next](#coming-next)

## Overview
Definitions:
* *Source*: represents the source technology, where the data model is defined (typically an ORM/ODM library).
* *Formatter*: an object that parses data models to a documentation format.
* *Sink*: a shared model (Pydantic class) that represents a bridge between source and formatter.

Basically, source entities are parsed and dumped to the sink.
Then, the formatter is provided as input to the formatter which generates the documentation.

![Architecture of dmdoc-python](docs/dmdoc-python.architecture.drawio.png)

Using the sink makes easier to add new sources or output formats, because there is no need to write code to parse
all combinations of sources and formats.

## Usage

### Installation
To install the package inside a new Python venv run the following:
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

### CLI
The CLI entry point is `dmdoc`. In the following sections are described available commands.

A command help is available too:
```bash
dmdoc --help
```

#### generate
The main command, used to generate documentation.

Usage:
```bash
dmdoc generate -s "path/to/source/config.yaml" -f "path/to/source/config.yaml"
```

### Extending dmdoc
## Sources
### Beanie
### SQLAlchemy
## Formatters
### Markdown
## Data types
List of available data types:

## Coming next
The project is developed on need. Thus, it lacks of the following features:
* Support for OGM. The sink model does not fit very well with graph schemas: a refactoring might be needed.
* Support for polymorphic object types. The sink model, as well as sources and formatters, does not support polymorphic objects.
* Exhaustive data types for Beanie and SQLAlchemy. Both sources are not widely tested and used, some data types are not mapped.
