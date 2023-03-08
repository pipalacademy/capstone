create table site (
    id serial primary key,
    name text unique not null,
    title text not null,
    domain text not null,

    created timestamp default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp default (CURRENT_TIMESTAMP at time zone 'utc'),

    CONSTRAINT ck_name CHECK (name ~ '^[a-z0-9-]+$')
);

-- create table site_settings (
--     id serial primary key,
--     site_id integer not null references site,
--     name text,
--     value text,

--     unique (site_id, name)
-- );

create table user (
    id integer primary key,
    site_id integer not null references site,
    username text not null,
    email_address text not null,
    full_name text,
    enc_password text,
    created timestamp default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp default (CURRENT_TIMESTAMP at time zone 'utc'),
);

create unique index user_username_idx on user(lower(username));
create unique index user_email_idx on user(lower(email));

create table project (
    id serial primary key,
    site_id integer not null references site,
    name text not null,
    short_description text not null,
    description text not null,
    tags text[],

    -- or status draft/published/archived
    is_published boolean default 'f',

    created timestamp default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp default (CURRENT_TIMESTAMP at time zone 'utc'),

    unique (site_id, name),
    CONSTRAINT ck_name CHECK (name ~ '^[a-z0-9-]+$')
);

create table task (
    id serial primary key,
    project_id integer not null references project,
    position integer not null,
    name text not null,
    title text not null,
    description text not null,

    CONSTRAINT ck_name CHECK (name ~ '^[a-z0-9-]+$'),
    unique(project_id, name)
);

create table check (
    id serial primary key,
    task_id integer not null references task,
    position integer not null,
    name text not null,
    title text not null,
    args JSON not null
);

-- create table changelog (
--     id serial primary key,
--     site_id integer not null references site,
--     project_id integer references project,
--     action text,
--     -- author
--     details JSON
-- );

-- user_project:
--     - project_id
--     - user_id
--     - git_url
--     - created
--     - last_modified

-- user_task_status
--     - task_id
--     - user_id
--     - status
--     - created
--     - last_modified

-- user_check_status
--     - status -- pending|pass|fail|error
--     - message text

-- How to handle deletes
--