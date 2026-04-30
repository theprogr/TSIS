# TSIS1 PhoneBook — Extended Contact Management

## Requirements

Install PostgreSQL and psycopg2:

```bash
pip install psycopg2-binary
```

## Database config

The password is already set in `config.py`:

```python
password = "12345678"
```

Database name is `postgres`.

## Run

From the TSIS1 folder:

```bash
python phonebook.py
```

The Python program can automatically run `schema.sql` and `procedures.sql` from menu option 1.

## Files

- `phonebook.py` — main console program
- `config.py` — database settings
- `connect.py` — connection function
- `schema.sql` — tables
- `procedures.sql` — stored procedures/functions
- `contacts.csv` — sample CSV import file