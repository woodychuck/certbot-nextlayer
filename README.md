certbot-nextlayer
============

next layer DNS Authenticator plugin for [Certbot](https://certbot.eff.org/).

This plugin is built from the ground up and follows the development style and life-cycle
of other `certbot-dns-*` plugins found in the
[Official Certbot Repository](https://github.com/certbot/certbot).

Installation
------------

```
pip install --upgrade certbot
pip install git+https://github.com/nextlayergmbh/certbot-nextlayer.git
```

Verify:

```
$ certbot plugins --text

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
* certbot-nextlayer
Description: Obtain certificates using a DNS TXT record by using nextlayer DNS
API.
Interfaces: IAuthenticator, IPlugin
Entry point: certbot-nextlayer = certbot_nextlayer.nextlayer_dns:Authenticator

...
...
```

Configuration
-------------

The credentials file e.g. `~/nldns-credentials.ini` should look like this:

```
certbot_nextlayer_api_key=abcdefghijklmnop
```

Usage
-----


```
certbot --authenticator certbot-nextlayer --certbot-nextlayer-credentials ~/nldns-credentials.ini certonly -d nextlayer.at
```
