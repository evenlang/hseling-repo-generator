import os
from base64 import b64decode, b64encode
from flask import Flask, Blueprint, render_template, request, redirect, jsonify
from logging import getLogger
import jsonrpclib


app = Flask(__name__)
app.config['DEBUG'] = False
app.config['LOG_DIR'] = '/tmp/'
if os.environ.get('HSELING_WEB_GENERATOR_SETTINGS'):
    app.config.from_envvar('HSELING_WEB_GENERATOR_SETTINGS')

app.config['HSELING_API_ENDPOINT'] = os.environ.get('HSELING_API_ENDPOINT')
app.config['HSELING_RPC_ENDPOINT'] = os.environ.get('HSELING_RPC_ENDPOINT')


def get_server_endpoint():
    HSELING_API_ENDPOINT = app.config.get('HSELING_API_ENDPOINT')
    HSELING_RPC_ENDPOINT = app.config.get('HSELING_RPC_ENDPOINT')

    return HSELING_RPC_ENDPOINT


def get_jsonrpc_server():
    jsonrpc_endpoint = get_server_endpoint()
    return jsonrpclib.Server(jsonrpc_endpoint)


if not app.debug:
    import logging
    from logging.handlers import TimedRotatingFileHandler
    # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
    file_handler = TimedRotatingFileHandler(os.path.join(app.config['LOG_DIR'], 'hseling_web_generator.log'), 'midnight')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter('<%(asctime)s> <%(levelname)s> %(message)s'))
    app.logger.addHandler(file_handler)


log = getLogger(__name__)


@app.route('/healthz')
def healthz():
    app.logger.info('Health checked')
    return jsonify({"status": "ok", "message": "Application Generator - WEB"})


@app.route('/web/')
def index():
    a = int(request.args.get('a', 1))
    b = int(request.args.get('b', 2))

    server = get_jsonrpc_server()

    try:
        result = server.add(a, b)
    except ConnectionRefusedError:
        result = None

    return render_template('index.html.j2', result=result)


@app.route('/')
def index_redirect():
    return redirect('/web/')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8000)


__all__ = [app]
