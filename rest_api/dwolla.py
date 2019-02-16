from django.conf import settings
import dwollav2 as dwolla

def get_dwolla_client():
    client = dwolla.Client(
        id=settings.DWOLLA_API_KEY,
        secret=settings.DWOLLA_SECRET_KEY,
        environment='sandbox' if settings.USE_FAKE else 'production'
    )

    return client.Auth.client()
