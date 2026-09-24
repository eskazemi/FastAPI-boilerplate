from ipaddress import ip_address
from fastapi import Request

TRUSTED_PROXY_IPS = frozenset(
    {
        "127.0.0.1",
        "::1",
        "10.0.0.1",
    }
)

def _normalize_ip(value: str) -> str:
    return str(ip_address(value.strip()))


def _is_trusted_proxy(value: str) -> bool:
    try:
        return _normalize_ip(value) in {
            _normalize_ip(proxy_ip)
            for proxy_ip in TRUSTED_PROXY_IPS
        }
    except ValueError:
        return False


def get_client_ip(request: Request) -> str:
    peer_ip = request.client.host if request.client else ""

    if not peer_ip:
        raise ValueError("Client IP is not available.")

    if not _is_trusted_proxy(peer_ip):
        return _normalize_ip(peer_ip)

    x_forwarded_for = request.headers.get("x-forwarded-for")

    if x_forwarded_for:
        # اولین IP در X-Forwarded-For معمولاً Client IP است.
        first_ip = x_forwarded_for.split(",", maxsplit=1)[0].strip()

        try:
            return _normalize_ip(first_ip)
        except ValueError:
            pass

    x_real_ip = request.headers.get("x-real-ip")

    if x_real_ip:
        try:
            return _normalize_ip(x_real_ip)
        except ValueError:
            pass

    return _normalize_ip(peer_ip)


