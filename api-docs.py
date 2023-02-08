from pathlib import Path

import yaml


DOCS_DIR = Path("api-docs")


class APIDocsException(Exception):
    pass


def make_table(headers, rows):

    def make_row(items):
        return (
            "| " +
            " |".join(
                str(item).replace("\n\n", "\\n").replace("\n", " ")
                for item in items) +
            " |" +
            "\n"
        )

    table = ""
    table += make_row(headers)
    table += make_row("---" for _ in headers)
    for row in rows:
        table += make_row(row)

    return table


def make_attr_table(attrs, items):
    return make_table(
        [attr.replace("_", " ").title() for attr in attrs],
        [[getattr(item, attr) for attr in attrs]
         for item in items]
    )


def make_named_param_table(items):
    return make_attr_table(
        ["name", "example", "type", "required", "description"],
        items,
    )


def make_typed_param_table(items):
    return make_attr_table(
        ["type", "required", "example", "description"],
        items,
    )


class Resource:
    def __init__(self, name):
        self.name = name
        self.endpoints = []

    def add(self, endpoint):
        self.endpoints.append(endpoint)

    def render(self):
        result = f"# {self.name.title()}"
        result += "\n\n"
        result += "\n\n".join(
            endpoint.render() for endpoint in self.endpoints
        )

        return result


class Endpoint:
    def __init__(
            self,
            endpoint,
            method,
            title,
            description,
            authenticated,
            request,
            response,
            notes=""):
        self.endpoint = endpoint
        self.method = method
        self.title = title
        self.description = description
        self.authenticated = "Admin-only" if authenticated else "Open"
        self.request = Request(method=self.method, **request)
        self.response = Response(**response)
        self.notes = notes

    def make_example_url(self):
        params = [(p.name, p.example) for p in self.request.path_parameters]
        url = self.endpoint
        for name, example in params:
            url = url.replace(f"<{name}>", example)
        return url

    def make_example_headers(self):
        headers = []
        headers.append("Host: ...")
        if self.authenticated != "Open":
            headers.append("Authorization: Bearer ...")
        if self.request.body:
            headers.append("Content-Type: application/json")
        return headers

    def make_example(self):
        result = ""

        url = self.make_example_url()
        result += f"{self.method} {url}\n"

        result += "\n".join(self.make_example_headers())
        result += "\n"

        if self.request.body:
            result += self.request.body[0].example

        result += "---\n"
        result += "HTTP/1.1 200 OK\n"
        result += "Content-Type: application/json\n"
        result += "\n"
        result += self.response.example

        return result

    def render(self):
        result = f"## {self.title}\n\n"

        result += make_table(
            ["Method", "Endpoint", "Authentication"],
            [[f"**{self.method}**", f"`{self.endpoint}`", self.authenticated]])
        result += "\n\n" + self.description

        result += "\n\n"
        result += "### Example\n\n"
        result += "```\n" + self.make_example() + "```\n"

        result += "\n\n" + self.request.render()
        result += "\n\n### Response\n\n"
        result += "\n\n" + self.response.render()
        if self.notes:
            result += f"\n\n### Notes\n\n{self.notes}"
        return result


class Request:
    def __init__(self, method, path_parameters=[], query_parameters=[], body={}):
        self.method = method
        self.path_parameters = [NamedParameter(**props) for props in path_parameters]
        self.query_parameters = [NamedParameter(**props) for props in query_parameters]
        self.body = [TypedParameter(**body)] if body else []

    def render(self):
        result = ""

        result += "\n\n### Path parameters\n\n"
        if self.path_parameters:
            table = make_named_param_table(self.path_parameters)
            result += table
        else:
            result += "*This endpoint doesn't take any path parameters.*"

        # result += "\n\n#### Query parameters\n\n"
        # if self.query_parameters:
        # result += "\n\n".join(param.render() for param in self.query_parameters)
        if self.method != "GET":
            result += "\n\n### Request Body\n\n"
            if self.body:
                result += "\n\n".join(b.render() for b in self.body)
            else:
                result += "\n\n*This endpoint takes an empty body*\n\n"
        return result


class TypedParameter:
    def __init__(self, type, description="", required=None, example="", **rest):
        self.type = type
        self.description = description
        self.example = example
        self.required = "required" if required else "optional"

        if self.is_array():
            self._init_array(**rest)
        elif self.is_object():
            self._init_object(**rest)

    def _init_array(self, each):
        self.each = TypedParameter(**each)
        self.each_type = self.type[6:-1]

    def _init_object(self, properties):
        self.properties = [NamedParameter(**prop) for prop in properties]

    def is_array(self):
        return self.type.startswith("array")

    def is_object(self):
        return self.type == "object"

    def render(self):
        result = ""

        if self.is_array():
            result += f"Array where each item is a {self.each_type}:\n\n"
            result += self.each.render()
        elif self.is_object() and any(p.is_object() for p in self.properties):
            result += "**Object properties:**\n\n"
            for p in self.properties:
                result += p.render() + "\n\n"
        elif self.is_object():
            result += "**Object properties:**\n\n"
            result += make_named_param_table(self.properties) + "\n\n"
        else:
            result += make_typed_param_table([self]) + "\n\n"

        if (self.is_array() or self.is_object()) and self.example:
            result += "**Response Example:**\n\n"
            result += f"```json\n{self.example}\n```\n\n"

        return result


class NamedParameter(TypedParameter):
    def __init__(self, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)

    def render(self):
        return f"\n\n##### {self.name}\n\n" + super().render()


class Response(TypedParameter):
    pass


def get_resources(base_dir):
    for resource_dir in base_dir.glob("*/"):
        resource_name = resource_dir.name
        resource = Resource(resource_name)
        for endpoint in get_endpoints(resource_dir):
            resource.add(endpoint)
        yield resource


def get_endpoints(resource_dir):
    endpoint_files = resource_dir.glob("*.yml")
    for path in endpoint_files:
        with open(path) as f:
            endpoint_kwargs = yaml.safe_load(f)

        try:
            endpoint = Endpoint(**endpoint_kwargs)
        except Exception as e:
            raise APIDocsException(f"Error in {path}") from e
        else:
            yield endpoint


if __name__ == "__main__":
    resources = get_resources(DOCS_DIR)
    print(
        "\n\n".join(
            resource.render() for resource in resources
        )
    )
