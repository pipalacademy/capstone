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
    password text,
    created text,
    last_modified text
);

create table activity (
    id integer primary key,
    username text not null,
    project_name text not null,
    created text,
    last_modified text,
    unique(username, project_name)
);

create table task_activity (
    id integer primary key,
    activity_id integer,
    task_id integer,
    created text,
    last_modified text,
    unique(activity_id, task_id)
);
