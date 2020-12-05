"""Represents the attached message to be included in the connection record."""

from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import ATTACHED_MESSAGE


class MessagesAttach(AgentMessage):
    """Class representing the attached message."""

    class Meta:
        """Metadata for attached message class."""

        schema_class = "MessagesAttachSchema"
        message_type = ATTACHED_MESSAGE

    def __init__(
        self,
        *,
        tx_my_role:str = None,
        tx_their_role:str = None,
        **kwargs
    ):
        """
        Initialize the attached message object.

        Args:
            tx_my_role: My role in the connection - related to endorsement protocol
            tx_their_role: Their role in the connection - related to endorsement protocol
        """

        super().__init__(**kwargs)

        self.mime_type = "application/json"

        self.lastmod_time = "time"

        self.description = "The roles related to endorsement protocol"

        self.data = {
            "json": {
                "tx_my_role":[],
                "tx_their_role":[]
                },
            }       


class MessagesAttachSchema(AgentMessageSchema):
    """Attached Message schema class."""

    class Meta:
        """Attached message schema metadata."""

        model_class = MessagesAttach
        unknown = EXCLUDE

    mime_type = fields.Str(required=True)
    lastmod_time = fields.Str(required=True)
    description = fields.Str(required=True)
    data = fields.Dict(required=True)