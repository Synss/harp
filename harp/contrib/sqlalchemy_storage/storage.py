import hashlib

from sqlalchemy import alias, func, select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from harp import get_logger
from harp.contrib.sqlalchemy_storage.settings import SqlAlchemyStorageSettings
from harp.contrib.sqlalchemy_storage.tables import BlobsTable, MessagesTable, TransactionsTable, metadata
from harp.core.asgi.events import (
    EVENT_CORE_STARTED,
    EVENT_TRANSACTION_ENDED,
    EVENT_TRANSACTION_MESSAGE,
    EVENT_TRANSACTION_STARTED,
)
from harp.core.asgi.events.message import MessageEvent
from harp.core.asgi.events.transaction import TransactionEvent
from harp.core.event_dispatcher import IAsyncEventDispatcher
from harp.core.models.messages import Blob, Message
from harp.core.models.transactions import Transaction

transactions = alias(TransactionsTable, name="t")
messages = alias(MessagesTable, name="m")
LEN_TRANSACTIONS_COLUMNS = len(TransactionsTable.columns)

logger = get_logger(__name__)


class SqlAlchemyStorage:
    """
    Storage implementation using SQL Alchemy Core, with async drivers.

    Currently supported/tested database drivers:

    - aiosqlite (sqlite+aiosqlite://...)

    """

    engine: AsyncEngine
    """Reference to the sqlalchemy async engine, which is a gateway to the database connectivity, able to provide a
    connection used to execute queries."""

    def __init__(self, dispatcher: IAsyncEventDispatcher, settings: SqlAlchemyStorageSettings):
        self.settings = settings
        self.engine = create_async_engine(self.settings.url, echo=self.settings.echo)
        self.metadata = metadata

        dispatcher.add_listener(EVENT_CORE_STARTED, self._on_startup_create_database, priority=-20)
        dispatcher.add_listener(EVENT_TRANSACTION_STARTED, self._on_transaction_started)
        dispatcher.add_listener(EVENT_TRANSACTION_ENDED, self._on_transaction_ended)
        dispatcher.add_listener(EVENT_TRANSACTION_MESSAGE, self._on_transaction_message)

    def connect(self):
        """Shortcut to get a connection from the engine.

        Example::

            async with self.connect() as conn:
                result = await conn.execute(...)

        """
        return self.engine.connect()

    def begin(self):
        """Shortcut to get a transaction from the engine (similar to :meth:`connect`, but with a database transaction).

        Example::

            async with self.begin() as conn:
                result = await conn.execute(...)

        """
        return self.engine.begin()

    async def find_transactions(self, *, with_messages=False):
        """
        Implements :meth:`IStorage.find_transactions <harp.protocols.storage.IStorage.find_transactions>`.

        :param with_messages:
        :return:

        """
        query = select(transactions, messages)
        if with_messages:
            # query.add_columns(messages)
            query = query.outerjoin(messages, messages.c.transaction_id == transactions.c.id)
        query = query.order_by(transactions.c.started_at.desc()).limit(50)

        current_transaction = None
        async with self.connect() as conn:
            result = await conn.execute(query)
            for row in result.fetchall():
                # not the same transaction, build new one
                if current_transaction is None or current_transaction.id != row[0]:
                    _db_transaction = row[0:LEN_TRANSACTIONS_COLUMNS]
                    if current_transaction:
                        yield current_transaction
                    current_transaction = Transaction(
                        id=_db_transaction[0],
                        type=_db_transaction[1],
                        started_at=_db_transaction[2],
                        finished_at=_db_transaction[3],
                        ellapsed=_db_transaction[4],
                        messages=[],
                    )

                if with_messages and row[LEN_TRANSACTIONS_COLUMNS]:
                    _db_message = row[LEN_TRANSACTIONS_COLUMNS:]
                    current_transaction.messages.append(
                        Message(
                            id=_db_message[0],
                            transaction_id=_db_message[1],
                            kind=_db_message[2],
                            summary=_db_message[3],
                            headers=_db_message[4],
                            body=_db_message[5],
                            created_at=_db_message[6],
                        )
                    )

            if current_transaction:
                yield current_transaction

    async def get_blob(self, blob_id):
        """
        Retrieve a blob from the database, using its hash.
        Returns None if not found.

        :param blob_id: sha1 hash of the blob
        :return: Blob or None
        """
        async with self.connect() as conn:
            row = (await conn.execute(BlobsTable.select().where(BlobsTable.c.id == blob_id))).fetchone()

        if row:
            return Blob(id=row.id, data=row.data)

    async def _store_blob(self, conn, data):
        if not isinstance(data, bytes):
            data = data.encode()
        hash = hashlib.sha1(data).hexdigest()

        query = select(func.count()).where(BlobsTable.c.id == hash)

        if not await conn.scalar(query):
            from sqlite3 import IntegrityError

            try:
                await conn.execute(BlobsTable.insert().values(id=hash, data=data))
            except IntegrityError as e:
                logger.error(
                    "SQLite IntegrityError: %s (ignored for now as it just shows concurrency problems with sqlite, "
                    "which we are aware of)",
                    e,
                )
        return hash

    async def _on_startup_create_database(self, event: TransactionEvent):
        """Event handler to create the database tables on startup. May drop them first if configured to do so."""
        async with self.begin() as conn:
            if self.settings.drop_tables:
                await conn.run_sync(metadata.drop_all)
            await conn.run_sync(metadata.create_all)

    async def _on_transaction_started(self, event: TransactionEvent):
        """Event handler to store the transaction in the database."""
        async with self.begin() as conn:
            await conn.execute(
                TransactionsTable.insert().values(
                    id=event.transaction.id,
                    type=event.transaction.type,
                    started_at=event.transaction.started_at,
                )
            )

    async def _on_transaction_message(self, event: MessageEvent):
        async with self.begin() as conn:
            headers_blob_id = await self._store_blob(conn, event.message.serialized_headers)
            body_blob_id = await self._store_blob(conn, event.message.serialized_body)
            await conn.execute(
                MessagesTable.insert().values(
                    transaction_id=event.transaction.id,
                    kind=event.message.kind,
                    summary=event.message.serialized_summary,
                    headers=headers_blob_id,
                    body=body_blob_id,
                    created_at=event.message.created_at,
                )
            )

    async def _on_transaction_ended(self, event: TransactionEvent):
        async with self.begin() as conn:
            await conn.execute(
                TransactionsTable.update()
                .where(TransactionsTable.c.id == event.transaction.id)
                .values(
                    finished_at=event.transaction.finished_at,
                    ellapsed=event.transaction.ellapsed,
                )
            )