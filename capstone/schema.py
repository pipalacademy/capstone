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

    with db.transaction():
        initial_schema(schema)
        create_localhost_site(schema)
        add_constraint(schema, table_name="user_project",
                    constraint_name="user_project_user_id_project_id_key",
                    constraint_condition="UNIQUE(user_id, project_id)")
        fix_user_email_unique_constraint(schema)

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

def add_constraint(schema, table_name, constraint_name, constraint_condition):
    db = schema.db

    db.query("ALTER TABLE %s DROP CONSTRAINT IF EXISTS %s" % (table_name, constraint_name))
    db.query("ALTER TABLE %s ADD CONSTRAINT %s %s" % (table_name, constraint_name, constraint_condition))

def fix_user_email_unique_constraint(schema):
    table_user_account = schema.get_table("user_account")

    # already applied
    if "user_account_site_username_idx" in table_user_account.get_indexes():
        return

    db = schema.db
    db.query("drop index user_account_username_idx")
    db.query("drop index user_account_email_idx")

    db.query("""
        create unique index user_account_site_username_idx
        on user_account(site_id, lower(username))
    """)
    db.query("""
        create unique index user_account_site_email_idx
        on user_account(site_id, lower(email))
    """)
