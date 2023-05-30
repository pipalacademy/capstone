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

create unique index user_account_site_username_idx on user_account(site_id, lower(username));
create unique index user_account_site_email_idx on user_account(site_id, lower(email));

create type project_type as enum ('web', 'cli');
create type deployment_type as enum ('nomad', 'custom');
create table project (
    id serial primary key,
    site_id integer not null references site,
    name text not null,
    title text not null,
    short_description text not null,
    description text not null,
    tags text[] not null,
    project_type project_type not null default 'web',
    deployment_type deployment_type not null default 'nomad',

    -- or status draft/published/archived
    is_published boolean default 'f',

    -- TODO: making git_url unique would also need it to be non-nullable
    -- maybe make it non nullable and unique later?
    git_url text,
    repo_id text,

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
    repo_id text not null unique,
    app_settings json not null default '{}'::json,
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
    user_id integer references user_account,
    action text not null,
    details JSON not null default '{}'::json,
    timestamp timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

    CHECK (json_typeof(details) = 'object')
);

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
);

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
);

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
);

create table user_course (
    id serial primary key,
    course_id integer not null references course,
    user_id integer not null references user_account,

    created timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),
    last_modified timestamp not null default (CURRENT_TIMESTAMP at time zone 'utc'),

    unique(user_id, course_id)
);

-- How to handle deletes
--
