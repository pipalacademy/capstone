import requests
import logging

logger = logging.getLogger(__name__)

def run_check(base_url, check_name, context, arguments):
    check_url = f"{base_url}/{check_name}"
    logger.info("  Running check %s", check_url)
    logger.info("  Arguments %s", arguments)
    r = requests.post(
        check_url,
        json={
            "context": context,
            "arguments": arguments,
        }
    )
    logger.info("Response: %s", r.text)

    # TODO: raise exception
    if not r.ok:
        return {
            "status": "error",
            "message": f"got HTTP status code {r.status_code} from checks URL",
        }

    match (body := r.json()):
        case {"status": "pass"|"fail"|"error", "message": None|str()}:
            return body
        case _:
            return {
                "status": "error",
                "message": "did not get a well-formed response from checks URL"
            }
