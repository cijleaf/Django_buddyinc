from cronutils import ErrorSentry
from cronutils.error_handler import NullErrorHandler
from django.conf import settings
from raven.transport import HTTPTransport

from mysunbuddy.settings import SENTRY_DSN


def make_synchronous_error_sentry(tags=None):
    """Uses synchronous transport HTTPTransport in order to make error sentry reports"""
    if settings.TESTING:
        return NullErrorHandler()
    tags = tags or {}
    return ErrorSentry(SENTRY_DSN, sentry_client_kwargs={'tags': tags, 'transport': HTTPTransport})