"""Outbound scanner traffic: approved HTTPS origins, validated and pinned DNS.

This module intentionally does not wrap the application's LLM provider clients.
"""
import asyncio
import ipaddress
import os
import socket
import httpx

HTTPError = httpx.HTTPError
TimeoutException = httpx.TimeoutException
RequestError = httpx.RequestError


class TargetPolicyError(ValueError):
    pass


class TargetTransport(httpx.AsyncBaseTransport):
    def __init__(self, inner=None):
        self.inner = inner or httpx.AsyncHTTPTransport(retries=0)

    async def handle_async_request(self, request):
        url = request.url
        approved = {origin.strip().rstrip("/") for origin in os.getenv("SCAN_ALLOWED_ORIGINS", "").split(",") if origin.strip()}
        origin = str(url.copy_with(path="/", query=None, fragment=None)).rstrip("/")
        if url.scheme != "https" or url.userinfo or origin not in approved or url.port not in (None, 443):
            raise TargetPolicyError("Configure this HTTPS origin in SCAN_ALLOWED_ORIGINS before scanning")
        infos = await asyncio.get_running_loop().getaddrinfo(url.host, 443, type=socket.SOCK_STREAM)
        ips = sorted({info[4][0] for info in infos})
        if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
            raise TargetPolicyError("Scanner targets must resolve exclusively to public addresses")
        # Connect to the validated IP. Preserve the original Host and TLS identity.
        pinned = httpx.Request(request.method, url.copy_with(host=ips[0]), headers=request.headers,
                               stream=request.stream, extensions={**request.extensions, "sni_hostname": url.host})
        response = await self.inner.handle_async_request(pinned)
        if 300 <= response.status_code < 400:
            await response.aclose()
            raise TargetPolicyError("Scanner redirects are disabled")
        return response

    async def aclose(self):
        await self.inner.aclose()


class AsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        if kwargs.get("follow_redirects") or kwargs.get("proxy") or kwargs.get("mounts"):
            raise TargetPolicyError("Redirects and custom proxies are disabled for scanner traffic")
        inner = kwargs.pop("transport", None)
        kwargs.update(transport=TargetTransport(inner), trust_env=False, follow_redirects=False)
        super().__init__(*args, **kwargs)
