create table site (
    id integer primary key,
    name text unique,
    current_task text,
    score int,
    healthy int default 1,
    created text default CURRENT_TIMESTAMP,
    last_updated text default CURRENT_TIMESTAMP
);

create table site_userdata (
    id integer primary key,
    site_id references site (id),
    key text,
    value text
);

create table task (
    id integer primary key,
    site_id integer references site(id),
    name text,
    status text, -- pass, fail
    checks text, -- json
    timestamp text default CURRENT_TIMESTAMP
);

-- changelog maintains all the changes to an site
-- entries could be one of the following types
--   deployed
--   task-done
--   site-unhealthy
--   site-healthy
--   tasks-broken
create table changelog (
    id integer primary key,
    site_id integer references site(id),
    timestamp text default CURRENT_TIMESTAMP,
    type text,
    message text
);

create table user (
    id integer primary key,
    username text unique not null
);
