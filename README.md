# MS Solution

This project is designed to manage and store mass spectrometry data. 
It includes SQLAlchemy models for database interactions, Pydantic models for 
data validation and serialization, and a Streamlit app for data using
the client api.

## Structure

- `database/`
  - `database.py`: Contains basic data base definition.
  - `schema.py`: Contains the SQLAlchemy models for the database schema.
  - `pydantic_models.py`: Contains the Pydantic models for data validation and
   serialization.
  - `io.py`: Contains database input and output operations.
  - `fastapi.py`: Contains the database api endpoints.
  - `chem.py`: Functions for compound mass computation and formula manipulation.
- `ms/`
  - `io.py`: Contains a class to handle client-side file in and output (such as
  reading input files) and the client-side api to the database.
  - `utils.py`: Some utility functions.
- `app.py`: The Streamlit app for using the client api.
- `script.py`: A script showing the client-side database api.
- `README.md`: This file.

### Example

```
import ms.io as io

# Read from file and POST compounds
data_holder = io.DataHolder(api_url="http://127.0.0.1:8000") 
data_holder.read_compounds(file_path="data/compounds.xlsx")
data_holder.insert_compounds_in_db()

# Get compounds
data_holder.get_compounds_from_db()
```