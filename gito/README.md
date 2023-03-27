# Gito

Gito is a service for creating anonymous git repos.

Gito provide an API to create git repos with a secret URL. Anyone
who has access to the URL can read and write to the repo.

Gito also supports webhook per repository. The webhook is triggered on push events. They are implemented as post-receive hook in git. As of now only one hook is supported per repo.

## How to run

Set the root directory for repos.

```
export GITO_ROOT=/var/www/git
```

It defaults to `git` when not specified.

Run the service using:

```
$ python gito.py
```

## The API

### Create a new repo

```
POST /api/repos

{
    "name": "rajdhani"
}
---
201 Created

Location: /api/repos/abcd12345678
```

### Get repo info

```
GET /apis/repos/abcd12345678

{
    "id": "abcd12345678",
    "name": "rajdhani",
    "repo_name": "abcd12345678/rajdhani",
    "git_url": "https://git.pipal.in/abcd12345678/rajdhani",
}
```

### Delete a repo

```
DELETE /apis/repos/abcd12345678
---
200 OK
{}
```

### Get webhook

```
GET /apis/repos/abcd12345678/hook

{"url": "https://example.com/foo"}
```

### Set webhook

```
POST /apis/repos/abcd12345678/hook

{"url": "https://example.com/foo"}
```
