"""Database schema migrations for capstone.
"""
from toolkit.db import Schema
import web
from pathlib import Path
from . import config

def migrate():
    """Migrate the database
    """
    db = web.database(config.db_uri)
    schema = Schema(db)

    initial_schema(schema)
    create_localhost_site(schema)

def initial_schema(schema):
    # schema is already initialized
    if schema.has_table("site"):
        return

    load_schema(schema, "schema.sql")

def load_schema(schema, filename):
    """Loads schema from filename relative to this module.
    """
    path = Path(__file__).parent / filename
    q = path.read_text()
    schema.db.query(web.SQLQuery(q))

def create_localhost_site(schema):
    db = schema.db
    row = db.where("site", name="localhost").first()
    if not row:
        db.insert("site",
                  name="localhost",
                  domain="localhost",
                  title="localhost")