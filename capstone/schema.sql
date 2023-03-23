create table site (
    id serial primary key,
    name text unique not null,
    domain text unique not null,
    title text not null,

    created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

    CONSTRAINT ck_name CHECK (name ~ '^[a-z0-9-]+$')
);

create index site_domain_idx on site(domain);

-- create table site_settings (
--     id serial primary key,
--     site_id integer not null references site,
--     name text,
--     value text,

--     unique (site_id, name)
-- );

create table user_account (
    id serial primary key,
    site_id integer not null references site,
    username text not null,
    email text not null,
    full_name text,
    enc_password text,
    created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc')
);

create unique index user_account_username_idx on user_account(lower(username));
create unique index user_account_email_idx on user_account(lower(email));

create table project (
    id serial primary key,
    site_id integer not null references site,
    name text not null,
    title text not null,
    short_description text not null,
    description text not null,
    tags text[] not null,

    -- or status draft/published/archived
    is_published boolean default 'f',

    created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

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

create table task_check (
    id serial primary key,
    task_id integer not null references task,
    position integer not null,
    name text not null,
    title text not null,
    args JSON not null
);

create table user_project (
    id serial primary key,
    project_id integer not null references project,
    user_id integer not null references user_account,
    git_url text not null,
    created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

    unique(user_id, project_id)
);

create table user_task_status (
    id serial primary key,
    user_project_id integer not null references user_project,
    task_id integer not null references task,
    status text not null,
    created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

    unique(user_project_id, task_id),
    CHECK (status ~ '^(Pending|In Progress|Completed|Failing)$')
);

create table user_check_status (
    id serial primary key,
    user_task_status_id integer not null references user_task_status,
    task_check_id integer not null references task_check,
    status text not null,
    message text,
    created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

    unique(user_task_status_id, task_check_id),
    CHECK (status ~ '^(pending|pass|fail|error)$')
);

create table changelog (
    id serial primary key,
    site_id integer not null references site,
    project_id integer references project,
    action text not null,
    details JSON not null default '{}'::json,

    CHECK (jsonb_typeof(details) = 'object')
);

-- How to handle deletes
--
