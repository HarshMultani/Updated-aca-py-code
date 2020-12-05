"""Refused transaction response handler."""

from .....messaging.base_handler import (
    BaseHandler,
    BaseResponder,
    RequestContext,
)

from ..manager import TransactionManager, TransactionManagerError
from ..messages.refused_transaction_response import RefusedTransactionResponse


class RefusedTransactionResponseHandler(BaseHandler):
    """Handler class for Refused transaction response."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """
        Handle refused transaction response.

        Args:
            context: Request context
            responder: Responder callback
        """

        self._logger.debug(f"RefusedTransactionResponseHandler called with context {context}")
        assert isinstance(context.message, RefusedTransactionResponse)

        mgr = TransactionManager(context)
        try:
            await mgr.receive_refuse_response(context.message)
        except TransactionManagerError:
            self._logger.exception("Error receiving refused transaction response")
