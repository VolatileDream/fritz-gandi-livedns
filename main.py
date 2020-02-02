from flask import Flask, abort, request
app = Flask(__name__)

@app.route('/update')
def update_with_params():
  domain = request.args.get('domain', None)
  ip4 = request.args.get('ip4', None)
  ip6 = request.args.get('ip6', None)

  if not ip4 and not ip6:
    abort(400)

  return {
    'domain': domain,
    'ip4' : ip4,
    'ip6' : ip6,
  }


def create_app():
  return app
