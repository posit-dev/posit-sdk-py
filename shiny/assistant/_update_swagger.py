from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from typing_extensions import Any, NotRequired, TypedDict, TypeVar

here = Path(__file__).parent
T = TypeVar("T")


def find_value(root, path):
    """
    Find a value in an object graph.

    This function is used to follow the specified path through the object graph at root
    and return the item in the graph, if any, that the path refers to.

    :param root: the root of the object graph to traverse.
    :param path: the path through the graph to take.
    :return: the resulting value or None.
    """
    if isinstance(path, str):
        path = path.split("/")
    parent = root
    for part in path:
        if part in parent:
            parent = parent[part]
        else:
            return None
    return parent


def expand_refs(
    document, obj
) -> Any:  # Use `Any` for return type to hack around typing requirement
    """
    Expands `ref`s in the given object.

    Returns an object semantically equivalent to the original but with references expanded.

    Parameters
    ----------
    document
        the master swagger document containing the responses and definitions.
    obj
        is either a normal swagger object, a ref object, or a swagger object with a schema.
    """
    if isinstance(obj, list):
        return [expand_refs(document, item) for item in obj]
    elif isinstance(obj, dict):
        if "$ref" in obj:
            ref_path = obj["$ref"].strip("#/").split("/")
            ref_value = find_value(document, ref_path)
            if ref_value is None:
                raise RuntimeError(f"Reference {obj['$ref']} not found in the document.")
            return expand_refs(document, ref_value)
        else:
            return {key: expand_refs(document, value) for key, value in obj.items()}
    else:
        return obj


class SwaggerOperation(TypedDict, total=False):
    operationId: str
    tags: list[str]
    summary: str
    description: str
    parameters: list[dict[str, Any]]
    responses: dict[str, Any]


class SwaggerDocument(TypedDict):
    paths: NotRequired[dict[str, SwaggerOperation]]
    parameters: NotRequired[dict[str, Any]]
    responses: NotRequired[dict[str, Any]]
    definitions: NotRequired[dict[str, Any]]


def expand_all_references(document: SwaggerDocument) -> SwaggerDocument:
    """
    Expands all JSON references.

    Expands all references ($ref) in the merged swagger document by replacing them with
    their full definitions.

    This returns a new document with all references expanded.

    Arguments
    ---------
    document
        The dictionary representing the Swagger document to process

    Returns
    -------
    :
        The processed Swagger document with all references expanded.
    """
    ret_document = deepcopy(document)
    # List of error response keys to ignore
    error_responses = [
        "BadRequest",
        "Unauthorized",
        "PaymentRequired",
        "Forbidden",
        "NotFound",
        "Conflict",
        "APIError",
        "InternalServerError",
    ]

    # We need to expand refs in paths
    if "paths" in ret_document:
        for _path, operations in ret_document["paths"].items():
            for _method, operation in operations.items():
                if not isinstance(operation, dict):
                    continue
                # Expand refs in parameters
                if "parameters" in operation:
                    operation["parameters"] = expand_refs(ret_document, operation["parameters"])

                # Expand refs in responses
                if "responses" in operation:
                    for code, response in operation["responses"].items():
                        if "schema" in response and code not in error_responses:
                            response["schema"] = expand_refs(ret_document, response["schema"])

    # Expand refs in top-level parameters
    if "parameters" in ret_document:
        ret_document["parameters"] = expand_refs(ret_document, ret_document["parameters"])

    # Expand refs in top-level responses, ignoring error responses
    if "responses" in ret_document:
        for response_key, response_value in ret_document["responses"].items():
            if response_key not in error_responses:
                ret_document["responses"][response_key] = expand_refs(ret_document, response_value)

    # Expand refs in definitions
    if "definitions" in ret_document:
        ret_document["definitions"] = expand_refs(ret_document, ret_document["definitions"])

    return ret_document


def require_swagger():
    if not (here / "swagger.json").exists():
        import urllib.request

        urllib.request.urlretrieve(
            "https://docs.posit.co/connect/api/swagger.json",
            here / "_swagger.json",
        )

    import json

    with open(here / "_swagger.json") as f:
        doc = json.load(f)

    swagger = expand_all_references(doc)
    return swagger


class OperationDef(TypedDict):
    name: str
    tags: list[str]
    method: str
    route: str
    definition: dict[str, Any]


def transform_swagger_to_operation_dict(swagger_dict: SwaggerDocument) -> dict[str, OperationDef]:
    """
    Swagger to operation dictionary transformation.

    Transforms the structure of a Swagger dictionary to create a dictionary where each entry key is
    the operation ID and the value is the definition for that operation, including the HTTP verb
    and the route.

    Args:
        swagger_dict: The dictionary representing the Swagger document.

    Returns
    -------
    :
        A dictionary where each key is an operation ID and the value is the operation definition.
    """
    operation_dict = {}

    if "paths" in swagger_dict:
        for route, operations in swagger_dict["paths"].items():
            for method, operation in operations.items():
                if not isinstance(operation, dict):
                    continue
                if "operationId" in operation:
                    operation_id = operation["operationId"]
                    tags = operation["tags"] if "tags" in operation else []
                    # response_parent = operation["responses"]["200"] or operation["responses"]["204"]
                    # if response_parent and "response"
                    operation_dict[operation_id] = {
                        "name": operation_id,
                        "tags": tags,
                        "method": method,
                        "route": route,
                        "definition": operation,
                    }

    return operation_dict


def main():
    swagger = require_swagger()

    operations = transform_swagger_to_operation_dict(require_swagger())

    with open(here / "_swagger_prompt.md", "w") as f:
        f.write(
            "If an answer can not be resolved, suggest to the user that they can explore calling these API routes themselves. Never produce code that calls these routes as we do not know the return type or successful status codes.\n\nAPI Routes:\n"
            ""
        )

        for operation in operations.values():
            # print("Operation:", operation["name"])

            # "GET /v1/tasks/{id} Get task details"
            f.write(
                "* "
                + operation["method"].upper()
                + " "
                + operation["route"]
                + " "
                + operation["definition"]["summary"].replace("\n", " ").strip()
                + "\n",
            )


if __name__ == "__main__":
    main()
