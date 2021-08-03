import os
import time
import logging
import json

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, Api, Resource, abort

from support import load_user_data, init_state_machine, retrieveAllSms, deleteSms

_LOGGER = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

_LOGGER.error('Start')
@app.route('/sms', methods=['GET','POST'])

def home():
  content = request.get_json()
  _LOGGER.error(' \n')
  _LOGGER.error('Request Received')
  _LOGGER.error(json.dumps(content, indent=4, sort_keys=True))
  _LOGGER.error('End of Request')
  _LOGGER.error(' \n')
  return 'OK'

app.run(port='5000', host="0.0.0.0")

_LOGGER.error('STOP')
