create table projects (
    id integer primary key,
    name text unique,
    title text,
    short_description text,
    description text,
    is_active integer,
    tags text,
    checks_url text,
    created text,
    last_modified text
);

create table tasks (
    id integer primary key,
    project_id int references projects(id),
    name text,
    title text,
    description text,
    position int,
    checks text,
    created text,
    last_modified text,
    unique(project_id, name)
);

create table users (
    id integer primary key,
    username text unique,
    email_address text unique,
    full_name text,
    password text, -- TODO: rename this to show that it's encoded
    created text,
    last_modified text
);

create table activity (
    id integer primary key,
    user_id text not null,
    project_id text not null,
    created text,
    last_modified text,
    unique(user_id, project_id)
);

create view activity_view as
select
    users.username,
    projects.name as project_name,
    activity.id,
    activity.user_id,
    activity.project_id,
    activity.created,
    activity.last_modified
from activity
join users on users.id == activity.user_id
join projects on projects.id == activity.project_id;

create table task_activity (
    id integer primary key,
    activity_id integer,
    task_id integer,
    checks text,
    status text,
    created text,
    last_modified text,
    unique(activity_id, task_id)
);

create view task_activity_view as
select
    tasks.position,
    tasks.name,
    tasks.title,
    task_activity.id,
    task_activity.activity_id,
    task_activity.task_id,
    task_activity.checks,
    task_activity.status,
    task_activity.created,
    task_activity.last_modified
from task_activity
join tasks on tasks.id == task_activity.task_id;
