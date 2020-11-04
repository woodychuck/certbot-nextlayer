"""DNS Authenticator for nextlayer DNS."""

import logging

import zope.interface
import requests
from certbot import interfaces
from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins import dns_common_lexicon

logger = logging.getLogger(__name__)

ttl = 60


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """
    DNS Authenticator for nextlayer.
    This Authenticator uses the nextlayer DNS API to fulfill a dns-01 challenge.
    """

    description = (
        "Obtain certificates using a DNS TXT record by using nextlayer DNS API."
    )

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
        self.request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=60
        )
        add("credentials", help="nextlayer DNS credentials file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 challenge using "
            + "the nextlayer DNS API"
        )

    def _setup_credentials(self):
        self._configure_file(
            "credentials", "Absolute path to nextlayer DNS credentials file"
        )
        dns_common.validate_file_permissions(self.conf("credentials"))
        self.credentials = self._configure_credentials(
            "credentials",
            "nextlayer DNS credentials file",
            {"api-key": "nextlayer DNS API Key"},
        )

        self.request_headers["X-API-Key"] = self.credentials.conf("api-key")

    def create_txt_record(self, domain, name, content):
        data = {
            "rrsets": [
                {
                    "name": name + ".",
                    "type": "TXT",
                    "changetype": "REPLACE",
                    "ttl": ttl,
                    "records": [{"content": '"%s"' % (content), "disabled": False}],
                }
            ]
        }

        try:
            result = requests.patch(
                url="https://dns.nextlayer.at/api/v1/servers/localhost/zones/" + domain,
                headers=self.request_headers,
                json=data,
                timeout=15
            )
            self.notify_slaves(domain=domain)
        except (Exception) as e:
            raise errors.PluginError(e)

    def delete_txt_record(self, domain, name):
        data = {
            "rrsets": [
                {
                    "name": name + ".",
                    "type": "TXT",
                    "ttl": ttl,
                    "changetype": "DELETE",
                }
            ]
        }

        try:
            result = requests.patch(
                url="https://dns.nextlayer.at/api/v1/servers/localhost/zones/" + domain,
                headers=self.request_headers,
                json=data,
                timeout=15
            )
            self.notify_slaves(domain=domain)
        except (Exception) as e:
            raise errors.PluginError(e)

    def notify_slaves(self, domain):
        requests.put(
            url="https://dns.nextlayer.at/api/v1/servers/localhost/zones"
            + domain
            + "/notify",
            headers=self.request_headers,
            timeout=15
        )

    def _perform(self, domain, validation_name, validation):
        self.create_txt_record(domain=domain, name=validation_name, content=validation)

    def _cleanup(self, domain, validation_name, validation):
        self.delete_txt_record(domain, validation_name)
