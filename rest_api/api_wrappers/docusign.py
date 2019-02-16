import requests
import json

from django.conf import settings
from django.core.files.base import ContentFile


class DocuSignHelper(object):
    """DocuSign helper."""

    def __init__(self):
        self.username = settings.DOCUSIGN_USERNAME
        self.password = settings.DOCUSIGN_PASSWORD
        self.integrator_key = settings.DOCUSIGN_INTEGRATOR_KEY
        self.authenticate_string = (
            "<DocuSignCredentials>" + "<Username>" + self.username + "</Username>" +
            "<Password>" + self.password + "</Password>" +
            "<IntegratorKey>" + self.integrator_key + "</IntegratorKey>" +
            "</DocuSignCredentials>"
        )
        self.headers = {
            'X-DocuSign-Authentication': self.authenticate_string,
            'Accept': 'application/json'
        }
        url = settings.DOCUSIGN_BASE_URL + '/v2/login_information'
        data = self.get(url)
        loginInfo = data.get('loginAccounts', [])
        account = loginInfo[0]
        self.base_url = account['baseUrl']
        self.account_id = account['accountId']

    def get(self, url, to_json=True):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        if not to_json:
            return response.content
        return response.json()
    
    def post(self, url, body):
        response = requests.post(url, json.dumps(body), headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_sign_view_from_template(self, deal, return_url):
        """Get sign view from template."""
        self.create_envelope(deal)
        return self.send_envelope(deal, return_url)

    def create_envelope(self, deal):
        """Create envelope for DocuSign."""
        percent = round(100 * deal.quantity / deal.seller.average_monthly_credit)
        tabs = {
            "textTabs": [
                {"tabLabel": "full_name", "value": deal.seller.name},
                {"tabLabel": "telephone", "value": deal.seller.phone},
                {"tabLabel": "address", "value": deal.seller.address},
                {"tabLabel": "seller_billing_account", "value": deal.seller.utility_service_identifier},
                {"tabLabel": "meter_number", "value": deal.seller.meter_number},
                {"tabLabel": "app_id", "value": ""},
                {"tabLabel": "percent", "value": deal.seller.credit_to_sell_percent},
                {"tabLabel": "custom_name_1", "value": deal.buyer.name},
                {"tabLabel": "service_address_1", "value": deal.buyer.address},
                {"tabLabel": "billing_account_number_1", "value": deal.buyer.utility_service_identifier},
                {"tabLabel": "amount_net_metering_1", "value": percent},
            ],
            "radioGroupTabs": [
                {"groupName": "B-1", "radios": []},
                {"groupName": "B-2", "radios": []},
            ],
            "checkboxTabs": [
                {"tabLabel": "electric_company_no", "selected": "true"},
            ]
        }
        template_role = {
            "clientUserId": deal.seller.id,
            "name": deal.seller.name,
            "email": deal.seller.email,
            "tabs": tabs,
            "roleName": settings.DOCUSIGN_ROLE_NAME_SELLER
        }
        body = {
            "status": "sent",
            "emailSubject": "MySunBuddy Net Metering Signature",
            #"documents":[],
            #"recipients": [{}],
            "templateId": settings.DOCUSIGN_TEMPLATE_ID,
            "templateRoles": [template_role]
        }
        data = self.post(self.base_url + "/envelopes", body)
        deal.update(docusign_envelope_id=data["uri"])

    def send_envelope(self, deal, return_url):
        """Send envelope for DocuSign."""
        return_url += "?envelopeId=" + deal.docusign_envelope_id
        body = {
            'authenticationMethod': 'none',
            'clientUserId': deal.seller.id,
            'email': deal.seller.email,
            'userName': deal.seller.name,
            'returnUrl': return_url,
        }
        url = self.base_url + deal.docusign_envelope_id + "/views/recipient"
        data = self.post(url, body)
        return data["url"]

    def download_envelope(self, deal, envelope_uri):
        """ Download envelope. """
        deal.update(docusign_envelope_id=envelope_uri)
        data = self.get(self.base_url + envelope_uri + "/documents")
        envelope_docs = data.get('envelopeDocuments')
        if len(envelope_docs) != 2:
            raise Exception("Wrong number of documents returned")
        document, summary = envelope_docs
        if summary["type"] != "summary":
            raise Exception("Unexpected docusign return")
        url = self.base_url + document.get("uri")
        document_contents = ContentFile(self.get(url, to_json=False))
        deal.docusign_contract.save(envelope_uri + ".pdf", document_contents)
