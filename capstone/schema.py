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
        add_gito_repo_id_column_to_user_project(schema)
        add_git_url_column_to_project(schema)
        add_gito_repo_id_column_to_project(schema)
        add_changelog(schema)
        rename_gito_repo_id_to_repo_id(schema)
        add_app_settings_column_to_user_project(schema)
        add_courses_tables(schema)
        add_project_type_column(schema)
        add_deployment_type_column(schema)

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

def add_gito_repo_id_column_to_user_project(schema):
    db = schema.db
    user_project = schema.get_table("user_project")

    if (not user_project.has_column("gito_repo_id") and
            not user_project.has_column("repo_id")):
        db.query("ALTER TABLE user_project ADD COLUMN IF NOT EXISTS gito_repo_id text not null unique")

def add_git_url_column_to_project(schema):
    db = schema.db
    db.query("ALTER TABLE project ADD COLUMN IF NOT EXISTS git_url text")

def add_gito_repo_id_column_to_project(schema):
    db = schema.db
    project = schema.get_table("project")

    if (not project.has_column("gito_repo_id") and
            not project.has_column("repo_id")):
        db.query("ALTER TABLE project ADD COLUMN IF NOT EXISTS gito_repo_id text")

def add_changelog(schema):
    db = schema.db

    if schema.has_table("changelog"):
        return

    db.query("""
    create table changelog (
        id serial primary key,
        site_id integer not null references site,
        project_id integer references project,
        user_id integer references user_account,
        action text not null,
        details JSON not null default '{}'::json,
        timestamp timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

        CHECK (json_typeof(details) = 'object')
    )""")

def rename_gito_repo_id_to_repo_id(schema):
    db = schema.db

    if not schema.get_table("project").has_column("repo_id"):
        db.query("ALTER TABLE project RENAME COLUMN gito_repo_id TO repo_id")

    if not schema.get_table("user_project").has_column("repo_id"):
        db.query("ALTER TABLE user_project RENAME COLUMN gito_repo_id TO repo_id")

def add_app_settings_column_to_user_project(schema):
    db = schema.db

    if not schema.get_table("user_project").has_column("app_settings"):
        db.query("ALTER TABLE user_project ADD COLUMN IF NOT EXISTS app_settings JSON NOT NULL DEFAULT '{}'::json")

def add_courses_tables(schema):
    db = schema.db

    if not schema.has_table("course"):
        db.query("""\
        create table course (
            id serial primary key,
            site_id integer not null references site,
            name text not null,
            title text not null,
            description text not null,
            -- tags?

            created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
            last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

            unique (site_id, name),
            CONSTRAINT ck_name CHECK (name ~ '^[a-z0-9-]+$')
        )""")

        db.query("""
        create table module (
            id serial primary key,
            course_id integer not null references course,
            position integer not null,
            name text not null,
            title text not null,

            created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
            last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

            CONSTRAINT ck_name CHECK (name ~ '^[a-z0-9-]+$'),
            unique(course_id, name)
        )""")

        db.query("""
        create table lesson (
            id serial primary key,
            module_id integer not null references module,
            position integer not null,
            name text not null,
            title text not null,
            path text not null,

            created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
            last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

            CONSTRAINT ck_name CHECK (name ~ '^[a-z0-9-]+$'),
            unique(module_id, name)
        )""")

        db.query("""
        create table user_course (
            id serial primary key,
            course_id integer not null references course,
            user_id integer not null references user_account,

            created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
            last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

            unique(user_id, course_id)
        )""")


def add_project_type_column(schema):
    db = schema.db

    if not schema.get_table("project").has_column("project_type"):
        db.query("create type project_type as enum ('web', 'cli')")
        db.query("ALTER TABLE project ADD COLUMN project_type project_type not null default 'web'")


def add_deployment_type_column(schema):
    db = schema.db

    if not schema.get_table("project").has_column("deployment_type"):
        db.query("create type deployment_type as enum ('nomad', 'custom')")
        db.query("alter table project add column deployment_type deployment_type not null default 'nomad'")
        db.query("alter table project add column deployment_options json not null default '{}'::json")
