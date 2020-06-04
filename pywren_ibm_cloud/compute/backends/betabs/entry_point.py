#
# (C) Copyright IBM Corp. 2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import logging
import pkgutil
import sys
from pywren_ibm_cloud.version import __version__
from pywren_ibm_cloud.config import cloud_logging_config
from pywren_ibm_cloud.function import function_handler
from pywren_ibm_cloud.function import function_invoker
from pywren_ibm_cloud.config import extract_storage_config
from pywren_ibm_cloud.storage import InternalStorage
from pywren_ibm_cloud.config import JOBS_PREFIX, STORAGE_FOLDER
from pywren_ibm_cloud.utils import sizeof_fmt
from pywren_ibm_cloud.storage.utils import create_runtime_meta_key



cloud_logging_config(logging.DEBUG)
import json
logger = logging.getLogger('__main__')


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)  
    return d

def runtime_packages(storage_config):
    logger.info("Extracting preinstalled Python modules...")
    internal_storage = InternalStorage(storage_config)

    runtime_meta = dict()
    mods = list(pkgutil.iter_modules())
    runtime_meta['preinstalls'] = [entry for entry in sorted([[mod, is_pkg] for _, mod, is_pkg in mods])]
    python_version = sys.version_info
    runtime_meta['python_ver'] = str(python_version[0])+"."+str(python_version[1])
    
    activation_id = storage_config['activation_id']

    status_key = create_runtime_meta_key(JOBS_PREFIX, activation_id)
    logger.debug("Runtime metadata key {}".format(status_key))
    dmpd_response_status = json.dumps(runtime_meta)
    drs = sizeof_fmt(len(dmpd_response_status))
    logger.info("Storing execution stats - Size: {}".format(drs))
    internal_storage.put_data(status_key, dmpd_response_status)


def main(action, payload_decoded):
    logger.info ("Welcome to PyWren-Beta-BS entry point. Action {}".format(action))
         
    payload = binary_to_dict(payload_decoded)
    logger.info(payload)
    if (action == 'preinstals'):
        runtime_packages(payload)
        return {"Execution": "Finished"}
    
    os.environ['__PW_ACTIVATION_ID'] = payload['activation_id']
    if 'remote_invoker' in payload:
        logger.info("PyWren v{} - Starting invoker".format(__version__))
        function_invoker(payload)
    else:
        logger.info("PyWren v{} - Starting execution".format(__version__))
        function_handler(payload)

    return {"Execution": "Finished"}

if __name__ == '__main__':
    main(sys.argv[1:][0], sys.argv[1:][1])
