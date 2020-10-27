import configparser
import sys
import os
import time
from splunk_hec_handler import SplunkHecHandler
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging

# disable insecure warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class PiabTelemetry:
    def __init__(self):
        self.settings = {}

    def _getConfig(self,config_file,stanza,mode):
    
        self.cwd = os.getcwd()
        self.file = os.path.join(self.cwd, "etc", config_file)
        if not os.path.isfile(self.file):
            print('Config file does not exist, or is not readable - check')
            return None

        self.config = configparser.RawConfigParser()
        self.config.read(self.file)
        if not self.config.has_section(stanza):
            print('Error: Section does not exist in config file')
            return None

        self.auth_token = self.config.get('server','auth_token', fallback=None)
        if self.auth_token is None:
            print('Auth_Token Key is not found - Check')
            return None
        
        self.server_address = self.config.get('server', 'server', fallback=None)
        if self.server_address is None:
            print('Server Address is not found - Check')
            return None

        # Grab config settings
        self.piab_config = os.path.join(self.cwd, "piab.conf")
        if not os.path.isfile(self.piab_config):
            print('piab.conf not found - check')
            return None
    
        self.piab_file = configparser.RawConfigParser()
        self.piab_file.read(self.piab_config)
        self.company_name = self.piab_file.get('customer_environment','company_name', fallback=None)
        if self.company_name == None:
            print('Customer Name is not found - check')

        self.username = self.piab_file.get('phantom_settings', 'phantom_community_username', fallback=None)
        if self.username == None:
            print('Phantom Username not found - check')

        self.now = time.time()
        self.settings = {'auth_token': self.auth_token, 'server_address': self.server_address}
        self.record = {'time': self.now, 'username': self.username, 'customer': self.company_name, 'mode': mode}
        return self.settings, self.record


    def write(self,mode):
        """ Provided with a record of type dict, it will update usage statistics of Phantom in a box """
        
        self.settings, self.record = self._getConfig('splunk.conf','server',mode)
        if self.settings == None:
            return None

        self.logger = logging.getLogger('SplunkHec')
        self.logger.setLevel(logging.INFO)
        self.splunk_handler = SplunkHecHandler(self.settings['server_address'],self.settings['auth_token'],sourcetype='piab:usage', port=8088, proto='https', ssl_verify=False,source='piab:telemetry')
        self.logger.addHandler(self.splunk_handler)
        try:
            self.logger.info(self.record)
            return True
        except Exception as e:
            print('logging to splunk failed: {}'.format(e))
            return False

        