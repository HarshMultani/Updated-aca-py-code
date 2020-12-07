"""Endorse Transaction handling admin routes."""

from aiohttp import web
from aiohttp_apispec import (
    request_schema,
    docs,
    response_schema,
    querystring_schema,
    match_info_schema,
)
from marshmallow import fields, validate

from ....utils.tracing import AdminAPIMessageTracingSchema
from .manager import TransactionManager
from .transaction_record import TransactionRecord, TransactionRecordSchema
from ....connections.models.conn_record import ConnRecord

from ....messaging.models.openapi import OpenAPISchema
from ....messaging.valid import UUIDFour

from .transaction_types import TransactionTypes


class TransactionListSchema(OpenAPISchema):
    """Result schema for transaction list."""

    results = fields.List(
        fields.Nested(TransactionRecordSchema()),
        description="List of transaction records",
    )


class TransactionsListQueryStringSchema(OpenAPISchema):
    """Parameters and validators for transactions list request query string."""



class TranIdMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking transaction id."""

    tran_id = fields.Str(
        description="Transaction identifier", required=True, example=UUIDFour.EXAMPLE
    )

class TransactionTypeSchema(OpenAPISchema):
    transaction_type = fields.Str(
        description="Transaction Types",
        required=False,
        validate=validate.OneOf(
            [r.name for r in TransactionTypes if isinstance(r.value[0], int)] + ["reset"]
        ),
    )


class CreateTransactionRecordSchema(AdminAPIMessageTracingSchema):
    """Parameters and validators to create transaction request and record."""

    conn_id = fields.Str(
        description="Connection identifier", required=True, example=UUIDFour.EXAMPLE
    )
    """
    attr_names = fields.List(
        fields.Str(example="color"),
        description="A list of attributes for this Schema",
        required=True,
    )
    name = fields.Str(
        description="The name of the schema", required=True, example="Schema"
    )
    version = fields.Str(
        description="The verion of this schema", required=True, example="1.0"
    )
    """
    transaction_message = fields.Dict(required=False)



@docs(
    tags=["endorse-transaction"],
    summary="Query transactions",
)
@querystring_schema(TransactionsListQueryStringSchema())
@response_schema(TransactionListSchema(), 200)
async def transactions_list(request: web.BaseRequest):
    """
    Request handler for searching transaction records.

    Args:
        request: aiohttp request object

    Returns:
        The transaction list response

    """

    context = request.app["request_context"]

    tag_filter = {}
    post_filter = {}

    records = await TransactionRecord.query(
        context, tag_filter, post_filter_positive=post_filter, alt=True
    )
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(tags=["endorse-transaction"], summary="Fetch a single transaction record")
@match_info_schema(TranIdMatchInfoSchema())
@response_schema(TransactionRecordSchema(), 200)
async def transactions_retrieve(request: web.BaseRequest):
    """
    Request handler for fetching a single transaction record.

    Args:
        request: aiohttp request object

    Returns:
        The transaction record response

    """

    context = request.app["request_context"]
    transaction_id = request.match_info["tran_id"]

    record = await TransactionRecord.retrieve_by_id(context, transaction_id)
    result = record.serialize()

    return web.json_response(result)


@docs(
    tags=["endorse-transaction"],
    summary="For author to send a transaction request",
)
@request_schema(CreateTransactionRecordSchema())
@querystring_schema(TransactionTypeSchema())
@response_schema(TransactionRecordSchema(), 200)
async def transaction_record_create(request: web.BaseRequest):
    """
    Request handler for creating a new transaction record and request.

    Args:
        request: aiohttp request object

    Returns:
        The transaction record

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    body = await request.json()

    connection_id = body.get("conn_id")
    #tx_message
    #attr_names = body.get("attr_names")
    #name = body.get("name")
    #version = body.get("version")
    transaction_message = body.get("transaction_message")
    transaction_type = request.query.get("transaction_type")

    transaction_message_keys = transaction_message.keys()

    #if transaction_type == "SCHEMA" and  ("schema_name" not in transaction_message_keys or "schema_version" not in transaction_message_keys or "attributes" not in transaction_message_keys):
        #return web.json_response({"error": "You have selected transaction type as SCHEMA and given a wrong payload"})

    #if transaction_type == "CREDENTIAL_DEFINITION" and ("revocation_registry_size" not in transaction_message_keys or "schema_id" not in transaction_message_keys or "support_revocation" not in transaction_message_keys or "tag" not in transaction_message_keys):
        #return web.json_response({"error": "You have selected transaction type as CREDENTIAL_DEFINITION and given a wrong payload"})

    
    connection = await ConnRecord.retrieve_by_id(context, connection_id)

    transaction_mgr = TransactionManager(context)
    (transaction, transaction_request) = await transaction_mgr.create_request(
        #attr_names=attr_names,
        #name=name,
        #version=version,
        connection_id=connection_id,
        transaction_message=transaction_message,
        transaction_type=transaction_type
    )

    await outbound_handler(transaction_request, connection_id=connection.connection_id)

    return web.json_response(transaction.serialize())


@docs(
    tags=["endorse-transaction"],
    summary="For Endorser to endorse a particular transaction record",
)
@match_info_schema(TranIdMatchInfoSchema())
@response_schema(TransactionRecordSchema(), 200)
async def endorse_transaction_response(request: web.BaseRequest):
    """
    Request handler for creating an endorsed transaction response.

    Args:
        request: aiohttp request object

    Returns:
        The updated transaction record details

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    transaction_id = request.match_info["tran_id"]
    transaction = await TransactionRecord.retrieve_by_id(context, transaction_id)

    if transaction.state == "request" or transaction.state == "resend":

        transaction_mgr = TransactionManager(context)
        (
            transaction,
            endorsed_transaction_response,
        ) = await transaction_mgr.create_endorse_response(
            transaction=transaction, state="endorse"
        )

        await outbound_handler(
            endorsed_transaction_response, connection_id=transaction.connection_id
        )

        return web.json_response(transaction.serialize())

    else:
        return web.json_response({"error": "You cannot endorse this transaction as it is not in request or resend state"})


@docs(
    tags=["endorse-transaction"],
    summary="For Endorser to refuse a particular transaction record",
)
@match_info_schema(TranIdMatchInfoSchema())
@response_schema(TransactionRecordSchema(), 200)
async def refuse_transaction_response(request: web.BaseRequest):
    """
    Request handler for creating a refused transaction response.

    Args:
        request: aiohttp request object

    Returns:
        The updated transaction record details

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    transaction_id = request.match_info["tran_id"]
    transaction = await TransactionRecord.retrieve_by_id(context, transaction_id)

    if transaction.state == "request" or transaction.state == "resend":

        transaction_mgr = TransactionManager(context)
        (
            transaction,
            refused_transaction_response,
        ) = await transaction_mgr.create_refuse_response(
            transaction=transaction, state="refuse"
        )

        await outbound_handler(
            refused_transaction_response, connection_id=transaction.connection_id
        )

        return web.json_response(transaction.serialize())

    else:
        return web.json_response({"error":"You cannot refuse the transaction as it is not in request or resend state"})


@docs(
    tags=["endorse-transaction"],
    summary="For Author to cancel a particular transaction request",
)
@match_info_schema(TranIdMatchInfoSchema())
@response_schema(TransactionRecordSchema(), 200)
async def cancel_transaction(request: web.BaseRequest):
    """
    Request handler for cancelling a Transaction request.

    Args:
        request: aiohttp request object

    Returns:
        The updated transaction record details

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    transaction_id = request.match_info["tran_id"]
    transaction = await TransactionRecord.retrieve_by_id(context, transaction_id)

    if transaction.state != "endorse" and transaction.state != "refuse":

        transaction_mgr = TransactionManager(context)
        (
            transaction,
            cancelled_transaction_response,
        ) = await transaction_mgr.cancel_transaction(
            transaction=transaction, state="cancel"
        )

        await outbound_handler(
            cancelled_transaction_response, connection_id=transaction.connection_id
        )

        return web.json_response(transaction.serialize())

    else:
        return web.json_response({"error":"Thie transaction cannot be cancelled as the endorser has sent the response"})


@docs(
    tags=["endorse-transaction"],
    summary="For Author to resend a particular transaction request",
)
@match_info_schema(TranIdMatchInfoSchema())
@response_schema(TransactionRecordSchema(), 200)
async def transaction_resend(request: web.BaseRequest):
    """
    Request handler for resending a transaction request.

    Args:
        request: aiohttp request object

    Returns:
        The updates transaction record details

    """

    context = request.app["request_context"]
    outbound_handler = request.app["outbound_message_router"]

    transaction_id = request.match_info["tran_id"]
    transaction = await TransactionRecord.retrieve_by_id(context, transaction_id)

    if transaction.state != "endorse":

        transaction_mgr = TransactionManager(context)
        (
            transaction,
            resend_transaction_response,
        ) = await transaction_mgr.transaction_resend(
            transaction=transaction, state="resend"
        )

        await outbound_handler(
            resend_transaction_response, connection_id=transaction.connection_id
        )

        return web.json_response(transaction.serialize())

    else:
        return web.json_response({"error":"You cannot resend an endorsed transaction"})


async def register(app: web.Application):
    """Register routes."""

    app.add_routes(
        [
            web.get("/transactions", transactions_list, allow_head=False),
            web.get("/transactions/{tran_id}", transactions_retrieve, allow_head=False),
            web.post("/transactions/create-request", transaction_record_create),
            web.post("/transactions/{tran_id}/endorse", endorse_transaction_response),
            web.post("/transactions/{tran_id}/refuse", refuse_transaction_response),
            web.post("/transactions/{tran_id}/cancel", cancel_transaction),
            web.post("/transaction/{tran_id}/resend", transaction_resend),
        ]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "endorse-transaction",
            "description": "Endorse a Transaction",
        }
    )
