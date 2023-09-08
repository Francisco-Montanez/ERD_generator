# ERD Generator

A library to generate Entity-Relationship Diagrams from a database schema.


### Supported Databases

- PostgreSQL

## Installation

You can install this library by cloning the repository and running:

```bash
pip install .
```

## Usage

```python
from erd_generator import generate_erd

database_url = 'postgresql://username:password@localhost:5432/test_db'

generate_erd(database_url, 'public', ['authors', 'books', 'books_authors', 'publishers' ], 'results/ERD', False)
```

### Parameters:

- **database_url**: The connection URL for the database.

- **schema_name**: The specific schema name to reflect within the database.

- **tables_to_include**: A list of table names to include in the ERD. If not provided, all tables will be included.

- **output_directory**: Location to save the generated file.

- **cleanup**: Should the DOT file be removed once the image (PNG) is generated?

## Generated ERD

![ERD](results/ERD.png)