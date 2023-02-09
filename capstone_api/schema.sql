create table projects (
    id integer primary key,
    name text unique,
    title text,
    short_description text,
    description text,
    is_active integer,
    tags text,
    created text,
    last_modified text
);

create table tasks (
    id integer primary key,
    name text unique,
    title text,
    description text,
    project_id int,
    created text,
    last_modified
);

create table users (
    id integer primary key,
    username text unique,
    email_address text unique,
    full_name text,
    created text,
    last_modified text
);

create table activity (
    id integer primary key,
    username text,
    project_id id,
    project_name text,
    created text,
    last_modified text,
    unique(username, project_id)
);
