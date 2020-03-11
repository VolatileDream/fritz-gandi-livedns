from flask import Flask, abort, request
app = Flask(__name__)

import requests, json, config

gandi_api = 'https://api.gandi.net'
#gandi_api = 'http://localhost:5000'

def headers(api_key, d=None):
  h = {
    'Connection': None,
    #'User-Agent': 'curl/7.65.3',
    'Authorization': 'Apikey ' + api_key
  }
  if d is not None:
    h.update(d)
  return h

def ip_type(ip4=None, ip6=None):
  if ip4:
    return 'A'
  if ip6:
    return 'AAAA'
  raise Exception('Bad ip_type call')


def url(domain, subdomain, ip4=None, ip6=None):
  t = ip_type(ip4, ip6)
  return gandi_api + '/v5/livedns/domains/%s/records/%s/%s' % (domain, subdomain, t)
  

def update_registration(domain, subdomain, ip4=None, ip6=None):
  u = url(domain, subdomain, ip4, ip6)
  values = []
  if ip4:
    values.append(ip4)
  if ip6:
    values.append(ip6)
  if len(values) == 0:
    app.logger.error('No valid IPs passed to update_registration')
    return False

  h = headers(config.api_key)
  payload = {
    'rrset_name': subdomain,
    'rrset_type': ip_type(ip4, ip6),
    'rrset_ttl': 300,
    'rrset_values': values,
  }

  response = requests.put(u, json=payload, headers=headers(config.api_key))
  if response.status_code != 200 and response.status_code != 201:
    app.logger.error('Error updating ip for record: %s\n%s' % (u, response._content))
    return False

  return json.loads(response._content)


def current_registration(domain, subdomain, ip4=None, ip6=None):
  u = url(domain, subdomain, ip4, ip6)

  response = requests.get(u, headers=headers(config.api_key))
  if response.status_code != 200:
    app.logger.error('Error checking ip from record: %s\n%s' % (subdomain, response._content))
    return False

  j = json.loads(response._content)
  return j


def try_update_ip(domain, subdomain, ip4=None, ip6=None):
  t = ip_type(ip4, ip6)
  resp = current_registration(domain, subdomain, ip4=ip4, ip6=ip6)
  if not resp:
    app.logger.error('Unable to fetch current registration for type: %s' % t)
    return
  
  addrs = set(resp['rrset_values'])

  if (ip4 and ip4 not in addrs) or (ip6 and ip6 not in addrs):
    if not update_registration(domain, subdomain, ip4=ip4, ip6=ip6):
      app.logger.error('Unable to update: %s for %s.%s' %(t, subdomain, domain))
      return 'error'
    else:
      return 'updated'

  return 'no-update'


@app.route('/update')
def update_with_params():
  """Router is updating the ip addr.

  It's unclear exactly when/why the Fritz!Box invokes this endpoint,
  so we check if the parameters given match the current content of the
  DNS record, and update them if they don't.
  """
  domain = request.args.get('domain', None)
  subdomain = request.args.get('subdomain', None)
  ip4 = request.args.get('ip4', None)
  ip6 = request.args.get('ip6', None)

  if not domain or not subdomain or (not ip4 and not ip6):
    abort(400)

  status4 = 'not-provided'
  status6 = 'not-provided'

  if ip4:
    status4 = try_update_ip(domain, subdomain, ip4=ip4)

  if ip6:
    status6 = try_update_ip(domain, subdomain, ip6=ip6)


  return {
    'domain': domain,
    'subdomain': subdomain,
    'ip4' : status4,
    'ip6' : status6,
  }


@app.route('/current')
def get_current():
  domain = request.args.get('domain')
  subdomain = request.args.get('subdomain')
  ip4 = request.args.get('ip4', None)
  ip6 = request.args.get('ip6', None)
  if not domain or not subdomain or (not ip4 and not ip6):
    abort(400)
  return str(current_registration(domain, subdomain, ip4, ip6))


@app.route('/force')
def force_update():
  domain = request.args.get('domain')
  subdomain = request.args.get('subdomain')
  ip4 = request.args.get('ip4', None)
  ip6 = request.args.get('ip6', None)
  if not domain or not subdomain or (not ip4 and not ip6):
    abort(400)
  return update_registration(domain, subdomain, ip4=ip4, ip6=ip6)


@app.route('/echo')
def echo():
  return "echo"

def create_app():
  return app
