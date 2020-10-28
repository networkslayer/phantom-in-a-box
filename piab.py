import os
import sys
import argparse
import requests
from modules import logger
from pathlib import Path
from modules.PiabTelemetry import PiabTelemetry
from modules.CustomConfigParser import CustomConfigParser
from modules.TerraformController import TerraformController
from modules.VagrantController import VagrantController
from modules.PackerController import PackerController


# need to set this ENV var due to a OSX High Sierra forking bug
# see this discussion for more details: https://github.com/ansible/ansible/issues/34056#issuecomment-352862252
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

VERSION = 1


if __name__ == "__main__":
    # grab arguments
    parser = argparse.ArgumentParser(description="Build Script for Phantom-in-a-box")
    parser.add_argument("-m", "--mode", required=False, choices=['vagrant', 'terraform', 'packer'],
                        help="mode of operation, terraform/vagrant/packer, please see configuration for each at: https://github.com/networkslayer/phantom-in-a-box")
    parser.add_argument("-a", "--action", required=False, choices=['build', 'destroy', 'stop', 'resume', 'build_amis', 'destroy_amis'],
                        help="action to take on the range, defaults to \"build\", build/destroy/stop/resume/build-amis/destroy_amis allowed")
    parser.add_argument("-c", "--config", required=False, default="piab.conf",
                        help="path to the configuration file of pantom-in-a-box")
    parser.add_argument("-tf", "--test_file", required=False, type=str, default="", help='test file for test command')                    
    parser.add_argument("-lm", "--list_machines", required=False, default=False, action="store_true", help="prints out all available machines")
    parser.add_argument("-ami", required=False, default=False, action="store_true", help="use prebuilt packer amis with mode terraform")
    parser.add_argument("-v", "--version", default=False, action="store_true", required=False,
                        help="shows current piab version")

    # parse them
    args = parser.parse_args()
    ARG_VERSION = args.version
    mode = args.mode
    action = args.action
    #target = args.target
    config = args.config
    list_machines = args.list_machines
    packer_amis = args.ami
    test_file = args.test_file
    

    print("""
        888                     888                         
        888                     888                         
        888                     888                         
88888b. 88888b.  8888b. 88888b. 888888 .d88b. 88888b.d88b.  
888 "88b888 "88b    "88b888 "88b888   d88""88b888 "888 "88b 
888  888888  888.d888888888  888888   888  888888  888  888 
888 d88P888  888888  888888  888Y88b. Y88..88P888  888  888 
88888P" 888  888"Y888888888  888 "Y888 "Y88P" 888  888  888 
888                                                         
888                                                         
888 
    """)

    # parse config file
    piab_config = Path(config)
    if piab_config.is_file():
        print("using config at path {0}".format(piab_config))
        configpath = str(piab_config)
    else:
        print("ERROR: failed to find a config file at {0} ..exiting".format(piab_config))
        sys.exit(1)

    # Parse config
    parser = CustomConfigParser()
    config = parser.load_conf(configpath)

    log = logger.setup_logging(config['log_path'], config['log_level'])
    log.info("INIT -  piab v" + str(VERSION))

    if ARG_VERSION:
        log.info("version: {0}".format(VERSION))
        sys.exit(0)

    if not mode:
        log.error('ERROR: Specify Build Mode with -m ')
        sys.exit(1)

    if mode and not action and not list_machines:
        log.error('ERROR: Use -a to perform an action or -lm to list available machines')
        sys.exit(1)

    if mode != 'terraform' and action == 'test':
        log.error('ERROR: test action only supported by terraform.')
        sys.exit(1)

    if mode != 'packer' and (action == 'build_amis' or action == 'destroy_amis'):
        log.error('ERROR: action build_amis and destroy_amis can only be used with packer')
        sys.exit(1)

    if mode != 'terraform' and packer_amis:
        log.error('ERROR: parameter packer_amis can only be used with terraform.')
        sys.exit(1)

    if mode == 'packer' and action != 'build_amis' and action != 'destroy_amis':
        log.error('ERROR: packer can only be used with action build_amis and destroy_amis. To build phantom-in-a-box use mode terraform or vagrant.')
        sys.exit(1)

    # Reachability Check for Internal VPN
    try:
        r = requests.get('https://git.splunk.com/users/deking/repos/phantom_pov/raw/apps')
        if not r.status_code == 200:
            log.error('Phantom POV repo is not accessible - please ensure you login to the VPN before re-running')
            sys.exit(1)
    except Exception as e:
        log.error('Phantom POV repo is not accessible - please ensure you login to the VPN before re-running')
        sys.exit(1)

    if config['phantom_community_username'] == "yourname@splunk.com":
        log.error('Please enter your phantom community username and password to piab.conf - then rerun')
        sys.exit(1)
   
    telem = PiabTelemetry()
    telem.write(mode)

    if mode == 'terraform':
        controller = TerraformController(config, log, packer_amis)
    elif mode == 'vagrant':
        controller = VagrantController(config, log)
    elif mode == 'packer':
        controller = PackerController(config, log)
        if action == 'build_amis':
            controller.build_amis()
        elif action == 'destroy_amis':
            controller.destroy_amis()

    if list_machines:
        controller.list_machines()
        sys.exit(0)

    if action == 'build':
        controller.build()

    if action == 'destroy':
        controller.destroy()

    if action == 'stop':
        controller.stop()

    if action == 'resume':
        controller.resume()

    if action == 'test':
        controller.test(test_file)

