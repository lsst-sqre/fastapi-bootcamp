"""Exceptions for the FastAPI Bootcamp app."""

from safir.fastapi import ClientRequestError
from safir.slack.blockkit import SlackException, SlackMessage, SlackTextField

__all__ = [
    "ObserverNotFoundError",
]


class DemoInternalError(SlackException):
    """Raised when a demo internal error occurs.

    A `SlackException` subclass is a custom exception provided by Safir that
    sends a message to a Slack channel, though the webhook URL, when it's
    raised. You can use the `to_slack` method to format that Slack message.

    SlackException subclasses are used by internal application errors
    (i.e., a request *should* have worked given the validated inputs, but
    something unexpected happend). On the other hand, if the request can't
    be completed because the user inputs are invalid, use the
    `ClientRequestError` subclass instead (see below).

    In other words, use `SlackException` for 500-type erros and
    `ClientRequestError` for 400-type errors.

    Note: to use SlackException, you need to set up the SlackRouteErrorHandler
    middleware in the FastAPI application. See `src/fastapibootcamp/main.py`.
    """

    def __init__(self, msg: str, custom_data: str | None = None) -> None:
        """Initialize the exception."""
        super().__init__(msg)
        self.custom_data = custom_data

    def to_slack(self) -> SlackMessage:
        message = super().to_slack()
        if self.custom_data:
            message.fields.append(
                SlackTextField(heading="Data", text=self.custom_data)
            )
        return message


class ObserverNotFoundError(ClientRequestError):
    """Raised when an observing site is not found."""

    status_code = 404

    error = "unknown_observer"
