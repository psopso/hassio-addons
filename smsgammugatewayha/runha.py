import os
import time
import logging
import json

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, Api, Resource, abort

from support import load_user_data, init_state_machine, retrieveAllSms, deleteSms

_LOGGER = logging.getLogger(__name__)

configpath = '/data/options.json'

f = open(configpath, "r")
jsonconfig = json.loads(f.read())
f.close()


device = jsonconfig["device"];
port = jsonconfig["port"];
if not("nomodem" in jsonconfig):
  nomodem = "0"
else:
  nomodem = jsonconfig["nomodem"]


if nomodem == 1:
  _LOGGER.error(json.dumps(jsonconfig, indent=4, sort_keys=True))

if os.path.exists('gammu.config'):
  os.remove('gammu.config')
f = open('gammu.config','x')
f.write('[gammu]\n')
f.write('device = ' + device + '\n')
f.write('name = serial modem\n')
f.write('connection = at\n')
f.close()

if nomodem == 1:
  _LOGGER.error("device:"+device)
  _LOGGER.error("port:"+str(port))
  _LOGGER.error("nomodem:"+str(nomodem))

  app = Flask(__name__)
  api = Api(app)

  _LOGGER.error('Start')
  #time.sleep(600)
  @app.route('/sms', methods=['GET','POST'])
  def home():
    content = request.get_json()
#    content = request.data
    _LOGGER.error(' \n')
    _LOGGER.error('Request Received')
    _LOGGER.error(json.dumps(content, indent=4, sort_keys=True))
    _LOGGER.error('End of Request')
    _LOGGER.error(' \n')
#    _LOGGER.error(content)
    return 'OK'

  app.run(port='5000', host="0.0.0.0")

  _LOGGER.error('STOP')
else:
  exec(open('run.py').read())
