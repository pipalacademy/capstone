# Activity

## Create activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/users/<username>/projects/<project-name>` |Admin-only |


Signup a user for a project



#### Path parameters

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| username |string |required |eva |The unique username of the user |
| project-name |string |required |build-your-own-shell |The unique name of the project |


#### Body



*This endpoint takes an empty body*



### Response



**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. If a user is not enrolled in a project with this slug (or such a project doesn't exist), a 404 response will be returned.  |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |optional | |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| status |string |required |In Progress |Either "Completed" or "In Progress". |
| tasks |array[task_status] |required | |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
{
  "slug": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "status": "Completed",
  "tasks": [
    {
      "slug": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "slug": "write-a-parser",
      "position": 2,
      "title": "Write a parser",
      "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
      "status": "completed",
      "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
    }
  ]
}

```



### Notes

The request body should be empty.


## Activity in a particular project

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>/projects/<project-slug>` |Admin-only |


Returns the activity (progress) of the user on a particular project. Will return 404 if either the username or project-slug doesn't exist.



#### Path parameters

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| username |string |required |eva |The unique username to use to fetch details about a user. Username is case-insensitive. |
| project-slug |string |required |build-your-own-shell |The unique project slug for a project that the user has signed up for |


### Response



**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. If a user is not enrolled in a project with this slug (or such a project doesn't exist), a 404 response will be returned.  |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |optional | |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| status |string |required |In Progress |Either "Completed" or "In Progress". |
| tasks |array[task_status] |required | |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
{
  "user": {
    "username": "eva"
  },
  "project": {
    "slug": ...,
    "title": ...,
    "short_description": ...,
  },
  "progress": {
    "total_tasks": 10,
    "completed_tasks": 8,
    "percentage": 80.0,
    "status": "In Progress",
  },
  "tasks": [
    {
      "slug": "write-parser",
      "status": "Completed",
      "checks": [
        {
          "name": "test-case-1",
          "title": "Test Case 1",
          "status": "pass", # or fail (maybe pending too)
          "message": "...", # optional
        }
      ]
    },
    {}
  ]
}

{
  "slug": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "status": "Completed",
  "tasks": [
    {
      "slug": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "slug": "write-a-parser",
      "position": 2,
      "title": "Write a parser",
      "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
      "status": "completed",
      "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
    }
  ]
}

```



## Update project progress

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/users/<username>/projects/<project-slug>/tasks` |Admin-only |


This is invoked by the checker to update the progress on the project.



#### Path parameters

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| username |string |required |eva |The unique username of the user |
| project-slug |string |required |build-your-own-shell |The unique project slug for a project that the user has signed up for |


#### Body

**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| status |string |required |In Progress |Either "Completed" or "In Progress". |
| tasks |array[task_status] |required | |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
{
  "status": "Completed",
  "tasks": [
    {
      "slug": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "slug": "write-a-parser",
      "position": 2,
      "title": "Write a parser",
      "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
      "status": "completed",
      "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
    }
  ]
}

```



### Response



**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. If a user is not enrolled in a project with this slug (or such a project doesn't exist), a 404 response will be returned.  |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |optional | |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| status |string |required |In Progress |Either "Completed" or "In Progress". |
| tasks |array[task_status] |required | |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
{
  "slug": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "status": "Completed",
  "tasks": [
    {
      "slug": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "slug": "write-a-parser",
      "position": 2,
      "title": "Write a parser",
      "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
      "status": "completed",
      "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
    }
  ]
}

```



## List all projects that any user has signed up for

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/activity` |Admin-only |


Returns a JSON list of all projects that a user has signed up for, with details about the completion status



#### Path parameters

*This endpoint doesn't take any path parameters.*

### Response



Array where each item is a activity_with_username:

**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. If a user is not enrolled in a project with this slug (or such a project doesn't exist), a 404 response will be returned.  |
| username |string |required |eva |Username of the user whom this activity belongs to.  |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |optional | |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| tasks |array[task_status] |required | |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
# TODO: same format as list-user-projects
[
  {
    "slug": "build-your-own-shell",
    "username": "eva",
    "title": "Build your own Shell",
    "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
    "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
    "is_active": true,
    "tags": ["Python", "Unix"]
    "status": "Completed",
    "tasks": [
      {
        "slug": "stdin-and-stdout",
        "position": 1,
        "title": "Stdin and stdout",
        "description": "Take input from stdin and simply echo it to stdout in a loop.",
        "status": "completed",
        "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
      },
      {
        "slug": "write-a-parser",
        "position": 2,
        "title": "Write a parser",
        "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
        "status": "completed",
        "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
      }
    ]
  },
  {
    "slug": "rajdhani",
    "username": "alice",
    "title": "Rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "description": "We will learn SQL by building a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"],
    "status": "In Progress",
    "tasks": [
      {
        "slug": "enable-homepage",
        "position": 1,
        "title": "Enable homepage",
        "description": "Set `flag_homepage` in `config.py` to `true`.",
        "status": "in_progress",
        "status_description": "Test case 1: check flag: failed\n"
      },
      {
        "slug": "search-trains",  # doesn't have status because it's unattempted
        "position": 2,
        "title": "Implement trains search for two stations",
        "description": "Implement search_trains in db.py"
      }
    ]
  }
]

```



## List all projects that a user has signed up for

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>/projects` |Admin-only |


Returns a JSON list of all projects that a user has signed up for, with details about the completion status



#### Path parameters

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| username |string |required |eva |The unique username to use to fetch details about a user. Username is case-insensitive. |


### Response



Array where each item is a activity_teaser:

**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. If a user is not enrolled in a project with this slug (or such a project doesn't exist), a 404 response will be returned.  |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |optional | |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| tasks |array[task_status] |required | |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
# TODO: should be same as fetch-user format, but without tasks
[
  {
    "slug": "build-your-own-shell",
    "title": "Build your own Shell",
    "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
    "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
    "is_active": true,
    "tags": ["Python", "Unix"]
    "status": "Completed",
    "tasks": [
      {
        "slug": "stdin-and-stdout",
        "position": 1,
        "title": "Stdin and stdout",
        "description": "Take input from stdin and simply echo it to stdout in a loop.",
        "status": "completed",
        "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n",
      },
      {
        "slug": "write-a-parser",
        "position": 2,
        "title": "Write a parser",
        "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
        "status": "completed",
        "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n",
      }
    ],
  },
  {
    "slug": "rajdhani",
    "title": "Rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "description": "We will learn SQL by building a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"],
    "status": "In Progress",
    "tasks": [
      {
        "slug": "enable-homepage",
        "position": 1,
        "title": "Enable homepage",
        "description": "Set `flag_homepage` in `config.py` to `true`.",
        "status": "in_progress",
        "status_description": "Test case 1: check flag: failed\n",
      },
      {
        "slug": "search-trains",  #
        "position": 2,
        "title": "Implement trains search for two stations",
        "description": "Implement search_trains in db.py",
      },
    ]
  }
]

```



# Projects

## Fetch a single project by its unique slug

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/projects/<name>` |Open |


Fetch a single project by its unique slug. This will return a status 404 response when a project with this slug doesn't exist.



#### Path parameters

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| name |string |required |build-your-own-shell |The unique project name to get details for |


### Response



**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |required | |Whether the project is active and available for users to take up. |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| tasks |array[tasks] |required | |Array of tasks associated with this Project |


**Example:**

```json
# TODO: rename slug to name
{
  "slug": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "tasks": [
      {
        "name": "stdin-and-stdout",
        "title": "Stdin and stdout",
        "description": "Take input from stdin and simply echo it to stdout in a loop."
      },
      {
        "name": "write-a-parser",
        "title": "Write a parser",
        "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting."
      }
  ]
}

```



## Create a project

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **POST** |`/api/projects` |Admin-only |


Create a new project. The request body should have all the initial fields for the project.



#### Path parameters

*This endpoint doesn't take any path parameters.*

#### Body

**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. Should not exist already. If it does, response will be a 400 Bad Request. |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |optional | |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| tasks |array[tasks] |required | |Array of tasks associated with this Project |


**Example:**

```json
# TODO: no need to take position for tasks
{
  "slug": "build-your-own-shell",
  "title": "build your own shell",
  "short_description": "a short description of the project, in markdown format. this is displayed on the project's card on the home page and dashboard.",
  "description": "in this project, we will build a unix shell from scratch.\n\nwe'll use the python's `subprocess` library to build shell.\n\n# learning outcomes\n- unix\n- python\n",
  "tags": ["Python", "Unix"],
  "tasks": [
      {
        "slug": "stdin-and-stdout",
        "position": 1,
        "title": "stdin and stdout",
        "description": "take input from stdin and simply echo it to stdout in a loop."
      },
      {
        "slug": "write-a-parser",
        "position": 2,
        "title": "write a parser",
        "description": "write a parser for shell. this part of description can include *italic*, **bold**, `code`, and other markdown formatting."
      }
  ]
}

```



### Response



**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. Should not exist already. If it does, response will be a 400 Bad Request. |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |required | |Whether the project is active and available for users to take up. |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| tasks |array[tasks] |required | |Array of tasks associated with this Project |


**Example:**

```json
{
  "slug": "build-your-own-shell",
  "title": "build your own shell",
  "short_description": "a short description of the project, in markdown format. this is displayed on the project's card on the home page and dashboard.",
  "description": "in this project, we will build a unix shell from scratch.\n\nwe'll use the python's `subprocess` library to build shell.\n\n# learning outcomes\n- unix\n- python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "tasks": [
      {
        "slug": "stdin-and-stdout",
        "position": 1,
        "title": "stdin and stdout",
        "description": "take input from stdin and simply echo it to stdout in a loop."
      },
      {
        "slug": "write-a-parser",
        "position": 2,
        "title": "write a parser",
        "description": "write a parser for shell. this part of description can include *italic*, **bold**, `code`, and other markdown formatting."
      }
  ]
}

```



### Notes

This endpoint gives 200 OK on success, and could give a 422 error when the project with given name is already present.


## List all projects

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/projects/` |Open |


Returns a JSON list of all projects



#### Path parameters

*This endpoint doesn't take any path parameters.*

### Response



Array where each item is a project:

**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |required | |Whether the project is active and available for users to take up. |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |


**Example:**

```json
[
  {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "url": "https://.../api/projects/build-your-own-shell",
    "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
    "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
    "is_active": true,
    "tags": ["Python", "Unix"]
  },
  {
    "slug": "rajdhani",
    "title": "Rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "description": "We will learn SQL by building a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"]
  }
]

```



## Update a single project

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/projects/<project-slug>` |Admin-only |


Update a single project. Its ID is given by the slug, and the body should have all the project fields as a JSON. This will return a status 404 response when a project with this slug doesn't exist. This will return a status 400 response when the body doesn't have all the required fields.



#### Path parameters

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| project-slug |string |required |build-your-own-shell |The unique project slug to use to fetch details about a project. |


#### Body

**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required | |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard. example: Learn the internals of Unix system by building your own Unix shell.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |required | |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| tasks |array[tasks] |required | |Array of tasks associated with this Project |


**Example:**

```json
{
  "title": "build your own shell",
  "short_description": "a short description of the project, in markdown format. this is displayed on the project's card on the home page and dashboard.",
  "description": "in this project, we will build a unix shell from scratch.\n\nwe'll use the python's `subprocess` library to build shell.\n\n# learning outcomes\n- unix\n- python\n",
  "tags": ["Python", "Unix"],
  "tasks": [
      {
        "slug": "stdin-and-stdout",
        "position": 1,
        "title": "stdin and stdout",
        "description": "take input from stdin and simply echo it to stdout in a loop."
      },
      {
        "slug": "write-a-parser",
        "position": 2,
        "title": "write a parser",
        "description": "write a parser for shell. this part of description can include *italic*, **bold**, `code`, and other markdown formatting."
      }
  ]
}

```



### Response



**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| slug |string |required |build-your-own-shell |Project slug that can be used in API requests and URLs. Should not exist already. If it does, response will be a 400 Bad Request. |
| title |string |required |Build your own Shell |Human readable title of the project |
| short_description |string |required |Learn the internals of Unix system by building your own Unix shell. |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |string |required |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active |boolean |required | |Whether the project is active and available for users to take up. |
| tags |array[string] |required |["Python", "Unix"]  |Tags associated with this project. |
| tasks |array[tasks] |required | |Array of tasks associated with this Project |


**Example:**

```json
{ "slug": "build-your-own-shell", "title": "build your own shell",
  "short_description": "a short description of the project, in markdown format. this is displayed on the project's card on the home page and dashboard.",
  "description": "in this project, we will build a unix shell from scratch.\n\nwe'll use the python's `subprocess` library to build shell.\n\n# learning outcomes\n- unix\n- python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "tasks": [
      {
        "slug": "stdin-and-stdout",
        "position": 1,
        "title": "stdin and stdout",
        "description": "take input from stdin and simply echo it to stdout in a loop."
      },
      {
        "slug": "write-a-parser",
        "position": 2,
        "title": "write a parser",
        "description": "write a parser for shell. this part of description can include *italic*, **bold**, `code`, and other markdown formatting."
      }
  ]
}

```



# Users

## Get a user

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>` |Admin-only |


Fetch a single user by their unique username. This will return a status 404 response when a user with this username doesn't exist.



#### Path parameters

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| username |string |required |eva |The unique username to use to fetch details about a user. Username is case-insensitive. |


### Response



**Object properties:**

| Name |Type |Required |Example |Description |
| --- |--- |--- |--- |--- |
| username |string |required |eva |Unique username of this user |
| full_name |string |required |Eva Lu Ator |Full name of the user |
| email_address |string |required |evaluator@example.com |Email address of this user |


**Example:**

```json
{
  "username": "eva",
  "full_name": "Eva Lu Ator",
  "email_address": "evaluator@example.com"
}

```


