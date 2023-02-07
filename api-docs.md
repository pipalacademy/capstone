# Activity

## Create activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/users/<username>/projects/<project-name>` |Admin-only |


Signup a user for a project



#### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |
| project-name |build-your-own-shell |string |required |Project name |


#### Body



*This endpoint takes an empty body*



### Response



**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name that can be used in API requests and URLs. If a user is not enrolled in a project with this name (or such a project doesn't exist), a 404 response will be returned.  |
| title |Build your own Shell |string |required |Human readable title of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell. |string |required |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active | |boolean |optional |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |["Python", "Unix"]  |array[string] |required |Tags associated with this project. |
| status |In Progress |string |required |Either "Completed" or "In Progress". |
| tasks | |array[task_status] |required |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "status": "Completed",
  "tasks": [
    {
      "name": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "name": "write-a-parser",
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


## Get activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>/projects/<project-name>` |Admin-only |


Get activity of a user on a project



#### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |
| project-name |build-your-own-shell |string |required |Project name |


### Response



**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name that can be used in API requests and URLs. If a user is not enrolled in a project with this name (or such a project doesn't exist), a 404 response will be returned.  |
| title |Build your own Shell |string |required |Human readable title of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell. |string |required |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active | |boolean |optional |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |["Python", "Unix"]  |array[string] |required |Tags associated with this project. |
| status |In Progress |string |required |Either "Completed" or "In Progress". |
| tasks | |array[task_status] |required |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
# TODO: format change for activity
{
  "user": {
    "username": "eva"
  },
  "project": {
    "name": ...,
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
      "name": "write-parser",
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
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "status": "Completed",
  "tasks": [
    {
      "name": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "name": "write-a-parser",
      "position": 2,
      "title": "Write a parser",
      "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
      "status": "completed",
      "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
    }
  ]
}

```



## Update activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/users/<username>/projects/<project-name>/tasks` |Admin-only |


This is invoked by the checker to update the progress on the project.



#### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |
| project-name |build-your-own-shell |string |required |Project name |


#### Body

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| status |In Progress |string |required |Either "Completed" or "In Progress". |
| tasks | |array[task_status] |required |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
{
  "status": "Completed",
  "tasks": [
    {
      "name": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "name": "write-a-parser",
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

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name that can be used in API requests and URLs. If a user is not enrolled in a project with this name (or such a project doesn't exist), a 404 response will be returned.  |
| title |Build your own Shell |string |required |Human readable title of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell. |string |required |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active | |boolean |optional |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |["Python", "Unix"]  |array[string] |required |Tags associated with this project. |
| status |In Progress |string |required |Either "Completed" or "In Progress". |
| tasks | |array[task_status] |required |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "status": "Completed",
  "tasks": [
    {
      "name": "stdin-and-stdout",
      "position": 1,
      "title": "Stdin and stdout",
      "description": "Take input from stdin and simply echo it to stdout in a loop.",
      "status": "completed",
      "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
    },
    {
      "name": "write-a-parser",
      "position": 2,
      "title": "Write a parser",
      "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
      "status": "completed",
      "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
    }
  ]
}

```



## List all activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/activity` |Admin-only |


Get a list of all project activity



#### Path parameters

*This endpoint doesn't take any path parameters.*

### Response



Array where each item is a activity_with_username:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name that can be used in API requests and URLs. If a user is not enrolled in a project with this name (or such a project doesn't exist), a 404 response will be returned.  |
| username |eva |string |required |Username of the user whom this activity belongs to.  |
| title |Build your own Shell |string |required |Human readable title of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell. |string |required |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active | |boolean |optional |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |["Python", "Unix"]  |array[string] |required |Tags associated with this project. |
| tasks | |array[task_status] |required |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
# TODO: same format as list-user-projects
[
  {
    "name": "build-your-own-shell",
    "username": "eva",
    "title": "Build your own Shell",
    "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
    "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
    "is_active": true,
    "tags": ["Python", "Unix"]
    "status": "Completed",
    "tasks": [
      {
        "name": "stdin-and-stdout",
        "position": 1,
        "title": "Stdin and stdout",
        "description": "Take input from stdin and simply echo it to stdout in a loop.",
        "status": "completed",
        "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n"
      },
      {
        "name": "write-a-parser",
        "position": 2,
        "title": "Write a parser",
        "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
        "status": "completed",
        "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n"
      }
    ]
  },
  {
    "name": "rajdhani",
    "username": "alice",
    "title": "Rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "description": "We will learn SQL by building a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"],
    "status": "In Progress",
    "tasks": [
      {
        "name": "enable-homepage",
        "position": 1,
        "title": "Enable homepage",
        "description": "Set `flag_homepage` in `config.py` to `true`.",
        "status": "in_progress",
        "status_description": "Test case 1: check flag: failed\n"
      },
      {
        "name": "search-trains",  # doesn't have status because it's unattempted
        "position": 2,
        "title": "Implement trains search for two stations",
        "description": "Implement search_trains in db.py"
      }
    ]
  }
]

```



## List a user's activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>/projects` |Admin-only |


Get a list of user's activity in all projects they are enrolled in



#### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |


### Response



Array where each item is a activity_teaser:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name that can be used in API requests and URLs. If a user is not enrolled in a project with this name (or such a project doesn't exist), a 404 response will be returned.  |
| title |Build your own Shell |string |required |Human readable title of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell. |string |required |A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A longer description of the project in Markdown format. This is displayed on the Project's own page in the UI.  |
| is_active | |boolean |optional |Whether the project is active and available for users to take up. (optional, defaults to `true`) |
| tags |["Python", "Unix"]  |array[string] |required |Tags associated with this project. |
| tasks | |array[task_status] |required |Array of tasks associated with this Project along with the status of each task for this user. |


**Example:**

```json
# TODO: should be same as fetch-user format, but without tasks
[
  {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
    "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
    "is_active": true,
    "tags": ["Python", "Unix"]
    "status": "Completed",
    "tasks": [
      {
        "name": "stdin-and-stdout",
        "position": 1,
        "title": "Stdin and stdout",
        "description": "Take input from stdin and simply echo it to stdout in a loop.",
        "status": "completed",
        "status_description": "Test case 1: echo without spaces - passed\nTest case 2: echo with whitespace - passed\n",
      },
      {
        "name": "write-a-parser",
        "position": 2,
        "title": "Write a parser",
        "description": "Write a parser for shell. This part of description can include *italic*, **bold**, `code`, and other markdown formatting.",
        "status": "completed",
        "status_description": "Test case 1: parse simple - passed\nTest case 2: parse with quotes - passed\n",
      }
    ],
  },
  {
    "name": "rajdhani",
    "title": "Rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "description": "We will learn SQL by building a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"],
    "status": "In Progress",
    "tasks": [
      {
        "name": "enable-homepage",
        "position": 1,
        "title": "Enable homepage",
        "description": "Set `flag_homepage` in `config.py` to `true`.",
        "status": "in_progress",
        "status_description": "Test case 1: check flag: failed\n",
      },
      {
        "name": "search-trains",  #
        "position": 2,
        "title": "Implement trains search for two stations",
        "description": "Implement search_trains in db.py",
      },
    ]
  }
]

```



# Projects

## Get a project

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/projects/<name>` |Open |


Get a single project by its unique name.



#### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |


### Response



**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| tasks | |array[task] |required |Array of task objects contained in this project |


**Example:**

```json
{
  "name": "build-your-own-shell",
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

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |optional |Whether project is visible on projects page (default: `true`) |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| tasks | |array[task] |required |Array of tasks associated with this Project |


**Example:**

```json
# TODO: no need to take position for tasks
{
  "name": "build-your-own-shell",
  "title": "build your own shell",
  "short_description": "a short description of the project, in markdown format. this is displayed on the project's card on the home page and dashboard.",
  "description": "in this project, we will build a unix shell from scratch.\n\nwe'll use the python's `subprocess` library to build shell.\n\n# learning outcomes\n- unix\n- python\n",
  "tags": ["Python", "Unix"],
  "tasks": [
      {
        "name": "stdin-and-stdout",
        "position": 1,
        "title": "stdin and stdout",
        "description": "take input from stdin and simply echo it to stdout in a loop."
      },
      {
        "name": "write-a-parser",
        "position": 2,
        "title": "write a parser",
        "description": "write a parser for shell. this part of description can include *italic*, **bold**, `code`, and other markdown formatting."
      }
  ]
}

```



### Response



**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| tasks | |array[task] |required |Array of task objects contained in this project |


**Example:**

```json
{
  "name": "build-your-own-shell",
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

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |


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
    "name": "rajdhani",
    "title": "Rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "description": "We will learn SQL by building a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"]
  }
]

```



## Update a project

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/projects/<project-name>` |Admin-only |


Update a project.



#### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |


#### Body

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |optional |Whether project is visible on projects page (default: `true`) |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| tasks | |array[task] |required |Array of tasks associated with this Project |


**Example:**

```json
# TODO: no need to take position for tasks
{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
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



### Response



**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| tasks | |array[task] |required |Array of task objects contained in this project |


**Example:**

```json
{
  "name": "build-your-own-shell",
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



### Notes

The body should have all the project fields as a JSON. This will return a status 404 response when a project with this name doesn't exist. This will return a status 400 response when the body doesn't have all the required fields.

# Users

## Get a user

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>` |Admin-only |


Fetch a single user by their unique username. This will return a status 404 response when a user with this username doesn't exist.



#### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |The unique username to use to fetch details about a user. Username is case-insensitive. |


### Response



**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Unique username of this user |
| full_name |Eva Lu Ator |string |required |Full name of the user |
| email_address |evaluator@example.com |string |required |Email address of this user |


**Example:**

```json
{
  "username": "eva",
  "full_name": "Eva Lu Ator",
  "email_address": "evaluator@example.com"
}

```


