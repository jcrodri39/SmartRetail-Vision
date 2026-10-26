"""Origin / Referer defense for browser POST requests.

This is a same-origin check, NOT a substitute for synchronizer CSRF tokens.
Configure the public HTTPS origin in SMARTRETAIL_PUBLIC_ORIGIN behind a proxy.
"""
from urllib.parse import urlsplit


def normalized_origin(value: str | None) -> str | None:
    if not value or value == "null":
        return None
    try:
        url = urlsplit(value)
        if url.scheme not in {"http", "https"} or not url.hostname:
            return None
        if url.username or url.password:
            return None
        if url.port is not None and not (1 <= url.port <= 65535):
            return None
        host = url.hostname.lower()
        if ":" in host:
            host = f"[{host}]"
        default_port = (url.scheme == "http" and url.port == 80) or (url.scheme == "https" and url.port == 443)
        port = f":{url.port}" if url.port and not default_port else ""
        return f"{url.scheme}://{host}{port}"
    except ValueError:
        return None


def same_origin_request(expected_origin: str, origin: str | None, referer: str | None) -> bool:
    expected = normalized_origin(expected_origin)
    if expected is None:
        return False
    # Origin is authoritative when supplied; do not fall back on mismatches.
    if origin is not None:
        return normalized_origin(origin) == expected and urlsplit(origin).path in ("", "/")
    return normalized_origin(referer) == expected if referer else False
