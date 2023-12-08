from config.common import Configuration
from http_router import NotFoundError, Router

from harp.applications.proxy.controllers import HttpProxyController
from harp.core.asgi.messages.requests import ASGIRequest
from harp.core.asgi.messages.responses import ASGIResponse
from harp.core.models.transactions import Transaction
from harp.core.views.json import json
from harp.protocols.storage import IStorage


class DashboardController(HttpProxyController):
    storage: IStorage
    proxy_settings: Configuration

    def __init__(self, storage: IStorage, proxy_settings: Configuration):
        super().__init__("http://localhost:4999/", name="ui")
        self.router = self.create_router()
        self.storage = storage
        self.proxy_settings = proxy_settings

    def create_router(self):
        router = Router(trim_last_slash=True)
        router.route("/api/transactions")(self.list_transactions)
        router.route("/api/transactions/{transaction}")(self.get_transaction)
        router.route("/api/blobs/{blob}")(self.get_blob)
        router.route("/api/settings")(self.get_settings)
        return router

    async def __call__(self, request: ASGIRequest, response: ASGIResponse, *, transaction_id=None):
        try:
            match = self.router(request.path, method=request.method)
            return await match.target(request, response, **(match.params or {}))
        except NotFoundError:
            return await super().__call__(request, response, transaction_id=transaction_id)

    async def list_transactions(self, request, response):
        transactions = []
        async for transaction in self.storage.find_transactions(with_messages=True):
            transactions.append(transaction)
        return json(
            {
                "items": list(map(Transaction.to_dict, transactions)),
                "total": len(transactions),
                "limit": 50,
                "offset": 0,
                "page": 1,
                "pages": 1,
            }
        )

    async def get_transaction(self, request, response, transaction):
        return json(
            {
                "@type": "transaction",
                "@id": transaction,
            }
        )

    async def get_blob(self, request, response, blob):
        blob = await self.storage.get_blob(blob)

        if not blob:
            await response.start(status=404, headers={"content-type": "text/plain"})
            await response.body(b"Blob not found.")
            return

        await response.start(status=200, headers={"content-type": "application/octet-stream"})
        await response.body(blob.data)

    async def get_settings(self, request, response):
        return json(self.proxy_settings.values)
