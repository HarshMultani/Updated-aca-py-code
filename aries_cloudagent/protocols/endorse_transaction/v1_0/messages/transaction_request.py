"""Represents a transaction request message."""

from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import TRANSACTION_REQUEST, PROTOCOL_PACKAGE


HANDLER_CLASS = (
    f"{PROTOCOL_PACKAGE}.handlers"
    ".transaction_request_handler.TransactionRequestHandler"
)


class TransactionRequest(AgentMessage):
    """Class representing a transaction request message."""

    class Meta:
        """Metadata for a transaction request message."""

        handler_class = HANDLER_CLASS
        message_type = TRANSACTION_REQUEST
        schema_class = "TransactionRequestSchema"

    def __init__(
        self,
        *,
        #attr_names: list = [],
        #name: str = None,
        #version: str = None,
        transaction_id: str = None,
        signature_request: dict = None,
        timing: dict = None,
        transaction_type:str = None,
        messages_attach: dict = None,
        **kwargs,
    ):
        """
        Initialize the transaction request object.

        Args:
            attr_names: The name of attributes present in the schema transaction
            name: The name of schema
            version: The version of schema
            transaction_id: The transaction id of the transaction record
            signature_request: The signature that is requested
            timing: The time till the endorser should endorse/refuse a transaction
            messages_attach: The attached message describing the actual transaction
        """
        super().__init__(**kwargs)
        #self.attr_names = attr_names
        #self.name = name
        #self.version = version
        self.transaction_id = transaction_id
        self.signature_request = signature_request
        self.timing = timing
        self.transaction_type = transaction_type
        self.messages_attach = messages_attach


class TransactionRequestSchema(AgentMessageSchema):
    """Transaction request schema class."""

    class Meta:
        """Transaction request schema metadata."""

        model_class = TransactionRequest
        unknown = EXCLUDE

    #attr_names = fields.List(fields.Str(), required=False)
    #name = fields.Str(required=False)
    #version = fields.Str(required=False)
    transaction_id = fields.Str(required=False)
    signature_request = fields.Dict(required=False)
    timing = fields.Dict(required=False)
    transaction_type = fields.Str(required=False)
    messages_attach = fields.Dict(required=False)
