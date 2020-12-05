"""Handle transaction information interface."""

from marshmallow import fields

from ....messaging.models.base_record import (
    BaseExchangeRecord,
    BaseExchangeSchema,
)

from ....config.injection_context import InjectionContext


class TransactionRecord(BaseExchangeRecord):
    """Represents a single transaction record."""

    class Meta:
        """Transaction Record metadata."""

        schema_class = "TransactionRecordSchema"

    RECORD_ID_NAME = "transaction_id"
    CACHE_ENABLED = True
    TAG_NAMES = {"state", "thread_id", "connection_id", "transaction_type"}
    RECORD_TYPE = "transaction"
    STATE_INIT = "init"

    def __init__(
        self,
        *,
        transaction_id: str = None,
        _type: str = None,
        transaction_type:str = None,
        comment: str = None,
        signature_request: list = [],
        signature_response: list = [],
        timing: dict = {},
        formats: list = [],
        messages_attach: list = [],
        thread_id: str = None,
        connection_id: str = None,
        state: str = None,
        **kwargs,
    ):
        """Initialize a new TransactionRecord."""

        super().__init__(transaction_id, state or self.STATE_INIT, **kwargs)
        self._type = _type
        self.transaction_type = transaction_type
        self.comment = comment
        self.signature_request = signature_request
        self.signature_response = signature_response
        self.timing = timing
        self.formats = formats
        self.messages_attach = messages_attach
        self.thread_id = thread_id
        self.connection_id = connection_id

    @property
    def record_value(self) -> dict:
        """Accessor for the JSON record value generated for this credential exchange."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "signature_request",
                "timing",
                "formats",
                "messages_attach",
                "signature_response",
                "transaction_type"
            )
        }

    @classmethod
    async def retrieve_by_connection_and_thread(
        cls, context: InjectionContext, connection_id: str, thread_id: str
    ) -> "TransactionRecord":
        """Retrieve a transaction record by connection and thread ID."""
        cache_key = f"credential_exchange_ctidx::{connection_id}::{thread_id}"
        record_id = await cls.get_cached_key(context, cache_key)
        if record_id:
            record = await cls.retrieve_by_id(context, record_id)
        else:
            record = await cls.retrieve_by_tag_filter(
                context,
                {"thread_id": thread_id},
                {"connection_id": connection_id} if connection_id else None,
            )
            await cls.set_cached_key(context, cache_key, record._id)
        return record


class TransactionRecordSchema(BaseExchangeSchema):
    """Schema to allow serialization/deserialization of transaction records."""

    class Meta:
        """TransactionRecordSchema metadata."""

        model_class = "TransactionRecord"

    _id = fields.Str(
        required=False, description="Connection identifier", example="any_example"
    )
    _type = fields.Str(
        required=False,
        description="Transaction type",
        example="The type of transaction",
    )
    transaction = fields.Str(
        required=False,
        description="The type of transaction (Schema or a Credential Definition"
    )
    signature_request = fields.List(
        fields.Dict(),
        required=False,
    )
    signature_response = fields.List(fields.Dict(), required=False)
    timing = fields.Dict(required=False)
    formats = fields.List(fields.Dict(), required=False)
    messages_attach = fields.List(fields.Dict(), required=False)
    thread_id = fields.Str(required=False, description="Thread Identifier")
    connection_id = fields.Str(
        required=False,
        description="The connection identifier for thie particular transaction record",
    )
