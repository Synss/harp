"""
Initial implementation : https://trello.com/c/yCdcY7Og/1-5-http-proxy
"""
import os

import pytest

from harp.testing.base import BaseProxyTest, TestProxy
from harp.testing.http import parametrize_with_http_methods, parametrize_with_http_status_codes
from harp.utils.network import get_available_network_port


class TestAsgiProxyWithoutEndpoints(BaseProxyTest):
    """
    A proxy without configured endpoint will send back 404 responses.

    """

    @pytest.fixture
    def proxy(self):
        factory = self.create_proxy_factory()
        return factory.create()

    @pytest.mark.asyncio
    async def test_asgi_proxy_get_no_endpoint(self, proxy):
        response = await proxy.asgi_http_get("/")
        assert response["status"] == 404
        assert response["body"] == b"No endpoint found for port 80."
        assert response["headers"] == []


class TestAsgiProxyWithMissingStartup(BaseProxyTest):
    @pytest.fixture(scope="class")
    def proxy(self, test_api):
        factory = self.create_proxy_factory()
        proxy_port = get_available_network_port()
        factory.add(test_api.url, port=proxy_port, name="default")
        return factory.create(default_host="proxy.localhost", default_port=proxy_port)

    async def test_missing_lifecycle_startup(self, proxy):
        response = await proxy.asgi_http_get("/echo")
        assert response["status"] == 500
        assert response["body"] == (
            b"Unhandled server error: Cannot access service provider, the lifespan.startup asgi event probably never "
            b"went through."
        )
        assert response["headers"] == []


class TestAsgiProxyWithStubApi(BaseProxyTest):
    """
    A proxy with an endpoint configured will forward requests to the api, if it has been started first (see asgi's
    lifespan.startup event).

    """

    @pytest.fixture(scope="class")
    async def proxy(self, test_api):
        factory = self.create_proxy_factory()
        proxy_port = get_available_network_port()
        factory.add(test_api.url, port=proxy_port, name="default")
        proxy = factory.create(default_host="proxy.localhost", default_port=proxy_port)
        await proxy.asgi_lifespan_startup()
        return proxy

    @parametrize_with_http_methods(include_non_standard=True, exclude=("CONNECT", "HEAD"))
    async def test_all_methods(self, proxy: TestProxy, method):
        response = await proxy.asgi_http(method, "/echo")
        assert response["status"] == 200
        assert response["body"] == method.encode("utf-8") + b" /echo"
        assert response["headers"] == ((b"content-type", b"text/html; charset=utf-8"),)

    async def test_head_request(self, proxy: TestProxy):
        response = await proxy.asgi_http_head("/echo")
        assert response["status"] == 200
        assert response["body"] == b""
        assert response["headers"] == ((b"content-type", b"text/html; charset=utf-8"),)

    @parametrize_with_http_methods(include_having_request_body=True)
    async def test_requests_with_body(self, proxy: TestProxy, method):
        response = await proxy.asgi_http(method, "/echo/body", body=b"Hello, world.")
        assert response["status"] == 200
        assert response["body"] == method.encode("utf-8") + b" /echo/body\nb'Hello, world.'"
        assert response["headers"] == ((b"content-type", b"text/html; charset=utf-8"),)

    @parametrize_with_http_methods(include_having_request_body=True)
    async def test_requests_with_binary_body(self, proxy: TestProxy, method):
        body = bytes(os.urandom(8))
        response = await proxy.asgi_http(method, "/echo/body", body=body)
        assert response["status"] == 200
        assert response["body"] == method.encode("utf-8") + b" /echo/body\n" + repr(body).encode("ascii")
        assert response["headers"] == ((b"content-type", b"text/html; charset=utf-8"),)

    @parametrize_with_http_methods(include_having_response_body=True, include_maybe_having_response_body=True)
    async def test_requests_with_response_body(self, proxy: TestProxy, method):
        response = await proxy.asgi_http(method, "/binary")
        assert response["status"] == 200
        assert len(response["body"]) == 32
        assert response["headers"] == ((b"content-type", b"application/octet-stream"),)

    @parametrize_with_http_status_codes(include=(2, 3, 4, 5))
    @parametrize_with_http_methods(exclude={"CONNECT", "HEAD"})
    async def test_response_status(self, proxy: TestProxy, method, status_code):
        response = await proxy.asgi_http(method, f"/status/{status_code}")
        assert response["status"] == status_code

    @parametrize_with_http_methods(exclude={"CONNECT", "HEAD"})
    async def test_headers(self, proxy: TestProxy, method):
        response = await proxy.asgi_http(method, "/headers")
        assert response["headers"] == ((b"X-Foo", b"Bar"), (b"content-type", b"application/octet-stream"))
