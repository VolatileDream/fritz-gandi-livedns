# Fritz!Box Dynamic DNS for Gandi.net LiveDns

A small Flask service that accepts requests from the Fritz!Box
and forwards the information to Gandi.net's LiveDns service.

## Configuring the Fritz!Box

Enable DynDns:
  * Open the router (usually http://fritz.box)
  * Internet > Permit Access > DynDNS
  * Check "Use DynDNS"
  * "DynDNS Provider" = User-defined
  * "Update URL" = `"http://" + host_port + "/update?domain=" + domain + "&ip4=<ipaddr>&ip6=<ip6addr>&subdomain=" + subdomain`
  * "Domain name" = subdomain + "." + domain
  * "User name" = unused
  * "Password" = unused

## Configuring the service

You'll need an API Key from Gandi.net:
  * Login to Gandi.net
  * Account > Security > Generate API Key
  * Insert the api key into `config.py`

You need to setup the service with systemd / etc.
  * Copy `dyndns.service` into `/etc/systemd/system`
  * Edit dyndns.service with the user & directory you want to run it as.

## Using HTTPS?

Can the Fritz!Box be configured to talk to my local service using HTTPS?

Dunno. I would like to set that up, but I think it's a catch-22, because you
won't have a valid HTTPS certificate when you initially set everything up.
