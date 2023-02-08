# Activity

## Create activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/users/<username>/projects/<project-name>` |Admin-only |


Signup a user for a project

### Example

```
PUT /api/users/eva/projects/build-your-own-shell
Host: ...
Authorization: Bearer ...
---
HTTP/1.1 200 OK
Content-Type: application/json

{
  "user": {
    "username": "eva"
  },
  "project": {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "url": "https://capstone.example.com/api/projects/build-your-own-shell"
    "short_description": "Learn the internals of the Unix system by building your own shell.",
    "is_active": true,
    "tags": ["Unix", "Python"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  },
  "progress": {
    "total_tasks": 3,
    "completed_tasks": 1,
    "percentage": 33.33,
    "status": "In Progress",
  },
  "tasks": [
    {
      "name": "write-a-parser",
      "title": "Write a Parser",
      "status": "Completed",
      "checks": [
        {
          "name": "test-case-1",
          "title": "Test Case 1",
          "status": "pass",
          "message": "",
        },
        {
          "name": "test-case-2",
          "title": "Test Case 2",
          "status": "pass",
          "message": "",
        }
      ]
    },
    {
      "name": "handle-quotes",
      "title": "Handle quotes while parsing",
      "status": "In Progress",
      "checks": [
        {
          "name": "test-quotes",
          "title": "Test shell args with quotes", "status": "fail",
          "message": "Failed to parse quoted arg with single quote"
        }
      ]
    },
    {
      "name": "echo-input",
      "title": "Echo parsed input",
      "status": "Pending",
      "checks": [
        {
          "name": "echo-input-1",
          "title": "Test echo input",
          "status": "pending",
          "message": null,
        }
      ]
    }
  ]
}
```




### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |
| project-name |build-your-own-shell |string |required |Project name |


### Request Body



*This endpoint takes an empty body*



### Response



**Object properties:**



##### user

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |






##### project

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| url |https://capstone.example.com/api/projects/build-your-own-shell |string |required |API URL of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| created |2023-02-07T06:50:07.984844+00:00 |string |required |Creation timestamp as an ISO8601 date string |
| last_modified |2023-02-07T06:50:07.984844+00:00 |string |required |Last modified timestamp as an ISO8601 date string |






##### progress

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| total_tasks |3 |integer |required |Total number of tasks in the project |
| completed_tasks |1 |integer |required |Number of tasks completed by the user |
| percentage |33.33 |float |required |Completion percentage |
| status |Completed |string |required |Completion status of the task. One of "Completed", "In Progress", "Failing", and "Pending". |






##### tasks

Array where each item is a task_progress:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name | |string |required |Task name |
| title | |string |required |Task title |
| status | |string |required |Task status - one of "Completed", "In Progress", "Failing", and "Pending" |
| checks | |array |required | |




**Response Example:**

```json
{
  "user": {
    "username": "eva"
  },
  "project": {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "url": "https://capstone.example.com/api/projects/build-your-own-shell"
    "short_description": "Learn the internals of the Unix system by building your own shell.",
    "is_active": true,
    "tags": ["Unix", "Python"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  },
  "progress": {
    "total_tasks": 3,
    "completed_tasks": 1,
    "percentage": 33.33,
    "status": "In Progress",
  },
  "tasks": [
    {
      "name": "write-a-parser",
      "title": "Write a Parser",
      "status": "Completed",
      "checks": [
        {
          "name": "test-case-1",
          "title": "Test Case 1",
          "status": "pass",
          "message": "",
        },
        {
          "name": "test-case-2",
          "title": "Test Case 2",
          "status": "pass",
          "message": "",
        }
      ]
    },
    {
      "name": "handle-quotes",
      "title": "Handle quotes while parsing",
      "status": "In Progress",
      "checks": [
        {
          "name": "test-quotes",
          "title": "Test shell args with quotes", "status": "fail",
          "message": "Failed to parse quoted arg with single quote"
        }
      ]
    },
    {
      "name": "echo-input",
      "title": "Echo parsed input",
      "status": "Pending",
      "checks": [
        {
          "name": "echo-input-1",
          "title": "Test echo input",
          "status": "pending",
          "message": null,
        }
      ]
    }
  ]
}

```



## Get activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>/projects/<project-name>` |Admin-only |


Get activity of a user on a project

### Example

```
GET /api/users/eva/projects/build-your-own-shell
Host: ...
Authorization: Bearer ...
---
HTTP/1.1 200 OK
Content-Type: application/json

{
  "user": {
    "username": "eva"
  },
  "project": {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "url": "https://capstone.example.com/api/projects/build-your-own-shell"
    "short_description": "Learn the internals of the Unix system by building your own shell.",
    "is_active": true,
    "tags": ["Unix", "Python"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  },
  "progress": {
    "total_tasks": 3,
    "completed_tasks": 1,
    "percentage": 33.33,
    "status": "In Progress",
  },
  "tasks": [
    {
      "name": "write-a-parser",
      "title": "Write a Parser",
      "status": "Completed",
      "checks": [
        {
          "name": "test-case-1",
          "title": "Test Case 1",
          "status": "pass",
          "message": "",
        },
        {
          "name": "test-case-2",
          "title": "Test Case 2",
          "status": "pass",
          "message": "",
        }
      ]
    },
    {
      "name": "handle-quotes",
      "title": "Handle quotes while parsing",
      "status": "In Progress",
      "checks": [
        {
          "name": "test-quotes",
          "title": "Test shell args with quotes", "status": "fail",
          "message": "Failed to parse quoted arg with single quote"
        }
      ]
    },
    {
      "name": "echo-input",
      "title": "Echo parsed input",
      "status": "Pending",
      "checks": [
        {
          "name": "echo-input-1",
          "title": "Test echo input",
          "status": "pending",
          "message": null,
        }
      ]
    }
  ]
}
```




### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |
| project-name |build-your-own-shell |string |required |Project name |


### Response



**Object properties:**



##### user

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |






##### project

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| url |https://capstone.example.com/api/projects/build-your-own-shell |string |required |API URL of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| created |2023-02-07T06:50:07.984844+00:00 |string |required |Creation timestamp as an ISO8601 date string |
| last_modified |2023-02-07T06:50:07.984844+00:00 |string |required |Last modified timestamp as an ISO8601 date string |






##### progress

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| total_tasks |3 |integer |required |Total number of tasks in the project |
| completed_tasks |1 |integer |required |Number of tasks completed by the user |
| percentage |33.33 |float |required |Completion percentage |
| status |Completed |string |required |Completion status of the task. One of "Completed", "In Progress", "Failing", and "Pending". |






##### tasks

Array where each item is a task_progress:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name | |string |required |Task name |
| title | |string |required |Task title |
| status | |string |required |Task status - one of "Completed", "In Progress", "Failing", and "Pending" |
| checks | |array |required | |




**Response Example:**

```json
{
  "user": {
    "username": "eva"
  },
  "project": {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "url": "https://capstone.example.com/api/projects/build-your-own-shell"
    "short_description": "Learn the internals of the Unix system by building your own shell.",
    "is_active": true,
    "tags": ["Unix", "Python"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  },
  "progress": {
    "total_tasks": 3,
    "completed_tasks": 1,
    "percentage": 33.33,
    "status": "In Progress",
  },
  "tasks": [
    {
      "name": "write-a-parser",
      "title": "Write a Parser",
      "status": "Completed",
      "checks": [
        {
          "name": "test-case-1",
          "title": "Test Case 1",
          "status": "pass",
          "message": "",
        },
        {
          "name": "test-case-2",
          "title": "Test Case 2",
          "status": "pass",
          "message": "",
        }
      ]
    },
    {
      "name": "handle-quotes",
      "title": "Handle quotes while parsing",
      "status": "In Progress",
      "checks": [
        {
          "name": "test-quotes",
          "title": "Test shell args with quotes", "status": "fail",
          "message": "Failed to parse quoted arg with single quote"
        }
      ]
    },
    {
      "name": "echo-input",
      "title": "Echo parsed input",
      "status": "Pending",
      "checks": [
        {
          "name": "echo-input-1",
          "title": "Test echo input",
          "status": "pending",
          "message": null,
        }
      ]
    }
  ]
}

```



## Update activity tasks

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/users/<username>/projects/<project-name>/tasks` |Admin-only |


This is invoked by the checker to update the progress on the project

### Example

```
PUT /api/users/eva/projects/build-your-own-shell/tasks
Host: ...
Authorization: Bearer ...
Content-Type: application/json

[
  {
    "name": "write-a-parser",
    "checks": [
      {
        "name": "test-case-1",
        "status": "pass",
        "message": "",
      },
      {
        "name": "test-case-2",
        "status": "pass",
        "message": "",
      }
    ]
  },
  {
    "name": "handle-quotes",
    "checks": [
      {
        "name": "test-quotes",
        "status": "fail",
        "message": "Failed to parse quoted arg with single quote"
      }
    ]
  },
  {
    "name": "echo-input",
    "checks": [
      {
        "name": "echo-input-1",
        "status": "pending",
        "message": null,
      }
    ]
  }
]
---
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "name": "write-a-parser",
    "title": "Write a Parser",
    "status": "Completed",
    "checks": [
      {
        "name": "test-case-1",
        "title": "Test Case 1",
        "status": "pass",
        "message": "",
      },
      {
        "name": "test-case-2",
        "title": "Test Case 2",
        "status": "pass",
        "message": "",
      }
    ]
  },
  {
    "name": "handle-quotes",
    "title": "Handle quotes while parsing",
    "status": "In Progress",
    "checks": [
      {
        "name": "test-quotes",
        "title": "Test shell args with quotes", "status": "fail",
        "message": "Failed to parse quoted arg with single quote"
      }
    ]
  },
  {
    "name": "echo-input",
    "title": "Echo parsed input",
    "status": "Pending",
    "checks": [
      {
        "name": "echo-input-1",
        "title": "Test echo input",
        "status": "pending",
        "message": null,
      }
    ]
  }
]
```




### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |
| project-name |build-your-own-shell |string |required |Project name |


### Request Body

Array where each item is a task_progress:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name | |string |required |Task name |
| checks | |array |required | |


**Response Example:**

```json
[
  {
    "name": "write-a-parser",
    "checks": [
      {
        "name": "test-case-1",
        "status": "pass",
        "message": "",
      },
      {
        "name": "test-case-2",
        "status": "pass",
        "message": "",
      }
    ]
  },
  {
    "name": "handle-quotes",
    "checks": [
      {
        "name": "test-quotes",
        "status": "fail",
        "message": "Failed to parse quoted arg with single quote"
      }
    ]
  },
  {
    "name": "echo-input",
    "checks": [
      {
        "name": "echo-input-1",
        "status": "pending",
        "message": null,
      }
    ]
  }
]

```



### Response



Array where each item is a task_progress:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name | |string |required |Task name |
| title | |string |required |Task title |
| status | |string |required |Task status - one of "Completed", "In Progress", "Failing", and "Pending" |
| checks | |array |required | |


**Response Example:**

```json
[
  {
    "name": "write-a-parser",
    "title": "Write a Parser",
    "status": "Completed",
    "checks": [
      {
        "name": "test-case-1",
        "title": "Test Case 1",
        "status": "pass",
        "message": "",
      },
      {
        "name": "test-case-2",
        "title": "Test Case 2",
        "status": "pass",
        "message": "",
      }
    ]
  },
  {
    "name": "handle-quotes",
    "title": "Handle quotes while parsing",
    "status": "In Progress",
    "checks": [
      {
        "name": "test-quotes",
        "title": "Test shell args with quotes", "status": "fail",
        "message": "Failed to parse quoted arg with single quote"
      }
    ]
  },
  {
    "name": "echo-input",
    "title": "Echo parsed input",
    "status": "Pending",
    "checks": [
      {
        "name": "echo-input-1",
        "title": "Test echo input",
        "status": "pending",
        "message": null,
      }
    ]
  }
]

```



## List activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/activity` |Admin-only |


Get a list of all project activity

### Example

```
GET /api/activity
Host: ...
Authorization: Bearer ...
---
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "user": {
      "username": "eva"
    },
    "project": {
      "name": "build-your-own-shell",
      "title": "Build your own Shell",
      "url": "https://capstone.example.com/api/projects/build-your-own-shell"
      "short_description": "Learn the internals of the Unix system by building your own shell.",
      "is_active": true,
      "tags": ["Unix", "Python"],
      "created": "2023-02-07T06:50:07.984844+00:00",
      "last_modified": "2023-02-07T06:50:07.984844+00:00"
    },
    "progress": {
      "total_tasks": 3,
      "completed_tasks": 1,
      "percentage": 33.33,
      "status": "In Progress",
    }
  }
]
```




### Path parameters

*This endpoint doesn't take any path parameters.*

### Response



Array where each item is a activity_teaser:

**Object properties:**



##### user

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |






##### project

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| url |https://capstone.example.com/api/projects/build-your-own-shell |string |required |API URL of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| created |2023-02-07T06:50:07.984844+00:00 |string |required |Creation timestamp as an ISO8601 date string |
| last_modified |2023-02-07T06:50:07.984844+00:00 |string |required |Last modified timestamp as an ISO8601 date string |






##### progress

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| total_tasks |3 |integer |required |Total number of tasks in the project |
| completed_tasks |1 |integer |required |Number of tasks completed by the user |
| percentage |33.33 |float |required |Completion percentage |
| status |Completed |string |required |Completion status of the task. One of "Completed", "In Progress", "Failing", and "Pending". |




**Response Example:**

```json
[
  {
    "user": {
      "username": "eva"
    },
    "project": {
      "name": "build-your-own-shell",
      "title": "Build your own Shell",
      "url": "https://capstone.example.com/api/projects/build-your-own-shell"
      "short_description": "Learn the internals of the Unix system by building your own shell.",
      "is_active": true,
      "tags": ["Unix", "Python"],
      "created": "2023-02-07T06:50:07.984844+00:00",
      "last_modified": "2023-02-07T06:50:07.984844+00:00"
    },
    "progress": {
      "total_tasks": 3,
      "completed_tasks": 1,
      "percentage": 33.33,
      "status": "In Progress",
    }
  }
]

```



## List user activity

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>/projects` |Admin-only |


Get a list of user's activity in all projects they have signed up for

### Example

```
GET /api/users/eva/projects
Host: ...
Authorization: Bearer ...
---
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "user": {
      "username": "eva"
    },
    "project": {
      "name": "build-your-own-shell",
      "title": "Build your own Shell",
      "url": "https://capstone.example.com/api/projects/build-your-own-shell"
      "short_description": "Learn the internals of the Unix system by building your own shell.",
      "is_active": true,
      "tags": ["Unix", "Python"],
      "created": "2023-02-07T06:50:07.984844+00:00",
      "last_modified": "2023-02-07T06:50:07.984844+00:00"
    },
    "progress": {
      "total_tasks": 3,
      "completed_tasks": 1,
      "percentage": 33.33,
      "status": "In Progress",
    }
  }
]
```




### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |


### Response



Array where each item is a activity_teaser:

**Object properties:**



##### user

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |






##### project

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| url |https://capstone.example.com/api/projects/build-your-own-shell |string |required |API URL of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| created |2023-02-07T06:50:07.984844+00:00 |string |required |Creation timestamp as an ISO8601 date string |
| last_modified |2023-02-07T06:50:07.984844+00:00 |string |required |Last modified timestamp as an ISO8601 date string |






##### progress

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| total_tasks |3 |integer |required |Total number of tasks in the project |
| completed_tasks |1 |integer |required |Number of tasks completed by the user |
| percentage |33.33 |float |required |Completion percentage |
| status |Completed |string |required |Completion status of the task. One of "Completed", "In Progress", "Failing", and "Pending". |




**Response Example:**

```json
[
  {
    "user": {
      "username": "eva"
    },
    "project": {
      "name": "build-your-own-shell",
      "title": "Build your own Shell",
      "url": "https://capstone.example.com/api/projects/build-your-own-shell"
      "short_description": "Learn the internals of the Unix system by building your own shell.",
      "is_active": true,
      "tags": ["Unix", "Python"],
      "created": "2023-02-07T06:50:07.984844+00:00",
      "last_modified": "2023-02-07T06:50:07.984844+00:00"
    },
    "progress": {
      "total_tasks": 3,
      "completed_tasks": 1,
      "percentage": 33.33,
      "status": "In Progress",
    }
  }
]

```



## Get activity tasks

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>/projects/<project-name>/tasks` |Admin-only |


Get progress of all tasks for a user on a project

### Example

```
GET /api/users/eva/projects/build-your-own-shell/tasks
Host: ...
Authorization: Bearer ...
---
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "name": "write-a-parser",
    "title": "Write a Parser",
    "status": "Completed",
    "checks": [
      {
        "name": "test-case-1",
        "title": "Test Case 1",
        "status": "pass",
        "message": "",
      },
      {
        "name": "test-case-2",
        "title": "Test Case 2",
        "status": "pass",
        "message": "",
      }
    ]
  },
  {
    "name": "handle-quotes",
    "title": "Handle quotes while parsing",
    "status": "In Progress",
    "checks": [
      {
        "name": "test-quotes",
        "title": "Test shell args with quotes", "status": "fail",
        "message": "Failed to parse quoted arg with single quote"
      }
    ]
  },
  {
    "name": "echo-input",
    "title": "Echo parsed input",
    "status": "Pending",
    "checks": [
      {
        "name": "echo-input-1",
        "title": "Test echo input",
        "status": "pending",
        "message": null,
      }
    ]
  }
]
```




### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| username |eva |string |required |Username of user |
| project-name |build-your-own-shell |string |required |Project name |


### Response



Array where each item is a task_progress:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name | |string |required |Task name |
| title | |string |required |Task title |
| status | |string |required |Task status - one of "Completed", "In Progress", "Failing", and "Pending" |
| checks | |array |required | |


**Response Example:**

```json
[
  {
    "name": "write-a-parser",
    "title": "Write a Parser",
    "status": "Completed",
    "checks": [
      {
        "name": "test-case-1",
        "title": "Test Case 1",
        "status": "pass",
        "message": "",
      },
      {
        "name": "test-case-2",
        "title": "Test Case 2",
        "status": "pass",
        "message": "",
      }
    ]
  },
  {
    "name": "handle-quotes",
    "title": "Handle quotes while parsing",
    "status": "In Progress",
    "checks": [
      {
        "name": "test-quotes",
        "title": "Test shell args with quotes", "status": "fail",
        "message": "Failed to parse quoted arg with single quote"
      }
    ]
  },
  {
    "name": "echo-input",
    "title": "Echo parsed input",
    "status": "Pending",
    "checks": [
      {
        "name": "echo-input-1",
        "title": "Test echo input",
        "status": "pending",
        "message": null,
      }
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

### Example

```
GET /api/projects/build-your-own-shell
Host: ...
---
HTTP/1.1 200 OK
Content-Type: application/json

{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "url": "https://capstone.example.com/api/projects/build-your-own-shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "created": "2023-02-07T06:50:07.984844+00:00",
  "last_modified": "2023-02-07T06:50:07.984844+00:00",
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




### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |


### Response



**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| url |https://capstone.example.com/api/projects/build-your-own-shell |string |required |API URL of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| created |2023-02-07T06:50:07.984844+00:00 |string |required |Creation timestamp as an ISO8601 date string |
| last_modified |2023-02-07T06:50:07.984844+00:00 |string |required |Last modified timestamp as an ISO8601 date string |
| tasks | |array[task] |required |Array of task objects contained in this project |


**Response Example:**

```json
{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "url": "https://capstone.example.com/api/projects/build-your-own-shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "is_active": true,
  "tags": ["Python", "Unix"],
  "created": "2023-02-07T06:50:07.984844+00:00",
  "last_modified": "2023-02-07T06:50:07.984844+00:00",
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



## Create or update a project

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **PUT** |`/api/projects/<project-name>` |Admin-only |


Create a new project or update it if it already exists

### Example

```
PUT /api/projects/<project-name>
Host: ...
Authorization: Bearer ...
Content-Type: application/json

{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "tags": ["Python", "Unix"],
  "created": "2023-02-07T06:50:07.984844+00:00",
  "last_modified": "2023-02-07T06:50:07.984844+00:00",
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
---
HTTP/1.1 200 OK
Content-Type: application/json

{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "url": "https://capstone.example.com/api/projects/build-your-own-shell",
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




### Path parameters

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |


### Request Body

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


**Response Example:**

```json
{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
  "description": "In this project, we will build a Unix shell from scratch.\n\nWe'll use the Python's `subprocess` library to build shell.\n\n# Learning outcomes\n- Unix\n- Python\n",
  "tags": ["Python", "Unix"],
  "created": "2023-02-07T06:50:07.984844+00:00",
  "last_modified": "2023-02-07T06:50:07.984844+00:00",
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
| url |https://capstone.example.com/api/projects/build-your-own-shell |string |required |API URL of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| description |In this project, we will build a Unix shell from scratch.\nWe'll use the Python's `subprocess` library to build shell.\n# Learning outcomes - Unix - Python  |string |required |A long description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| created |2023-02-07T06:50:07.984844+00:00 |string |required |Creation timestamp as an ISO8601 date string |
| last_modified |2023-02-07T06:50:07.984844+00:00 |string |required |Last modified timestamp as an ISO8601 date string |
| tasks | |array[task] |required |Array of task objects contained in this project |


**Response Example:**

```json
{
  "name": "build-your-own-shell",
  "title": "Build your own Shell",
  "url": "https://capstone.example.com/api/projects/build-your-own-shell",
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

## List all projects

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/projects/` |Open |


Returns a JSON list of all projects

### Example

```
GET /api/projects/
Host: ...
---
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "url": "https://capstone.example.com/api/projects/build-your-own-shell",
    "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
    "is_active": true,
    "tags": ["Python", "Unix"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  },
  {
    "name": "rajdhani",
    "title": "Rajdhani",
    "url": "https://capstone.example.com/api/projects/rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  }
]
```




### Path parameters

*This endpoint doesn't take any path parameters.*

### Response



Array where each item is a project_teaser:

**Object properties:**

| Name |Example |Type |Required |Description |
| --- |--- |--- |--- |--- |
| name |build-your-own-shell |string |required |Project name |
| title |Build your own Shell |string |required |Human readable title of project |
| url |https://capstone.example.com/api/projects/build-your-own-shell |string |required |API URL of the project |
| short_description |Learn the internals of Unix system by building your own Unix shell |string |required |Short description in Markdown format  |
| is_active | |boolean |required |Whether project is visible on projects page |
| tags |["Python", "Unix"]  |array[string] |required |Project tags |
| created |2023-02-07T06:50:07.984844+00:00 |string |required |Creation timestamp as an ISO8601 date string |
| last_modified |2023-02-07T06:50:07.984844+00:00 |string |required |Last modified timestamp as an ISO8601 date string |


**Response Example:**

```json
[
  {
    "name": "build-your-own-shell",
    "title": "Build your own Shell",
    "url": "https://capstone.example.com/api/projects/build-your-own-shell",
    "short_description": "A short description of the project, in Markdown format. This is displayed on the Project's card on the home page and dashboard.",
    "is_active": true,
    "tags": ["Python", "Unix"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  },
  {
    "name": "rajdhani",
    "title": "Rajdhani",
    "url": "https://capstone.example.com/api/projects/rajdhani",
    "short_description": "Build a booking system for Indian railways",
    "is_active": true,
    "tags": ["Python", "Webapp", "Database"],
    "created": "2023-02-07T06:50:07.984844+00:00",
    "last_modified": "2023-02-07T06:50:07.984844+00:00"
  }
]

```



# Users

## Get a user

| Method |Endpoint |Authentication |
| --- |--- |--- |
| **GET** |`/api/users/<username>` |Admin-only |


Fetch a single user by their unique username. This will return a status 404 response when a user with this username doesn't exist.

### Example

```
GET /api/users/eva
Host: ...
Authorization: Bearer ...
---
HTTP/1.1 200 OK
Content-Type: application/json

{
  "username": "eva",
  "full_name": "Eva Lu Ator",
  "email_address": "evaluator@example.com"
}
```




### Path parameters

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


**Response Example:**

```json
{
  "username": "eva",
  "full_name": "Eva Lu Ator",
  "email_address": "evaluator@example.com"
}

```


