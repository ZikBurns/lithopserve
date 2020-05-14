import os
import tempfile
import multiprocessing
from pywren_ibm_cloud.config import LOGS_PREFIX


RUNTIME_NAME_DEFAULT = 'localhost'
RUNTIME_TIMEOUT_DEFAULT = 600  # 10 minutes

TEMP = tempfile.gettempdir()
STORAGE_BASE_DIR = os.path.join(TEMP)
LOCAL_LOGS_DIR = os.path.join(STORAGE_BASE_DIR, LOGS_PREFIX)


def load_config(config_data):
    config_data['pywren']['runtime'] = RUNTIME_NAME_DEFAULT
    config_data['pywren']['runtime_memory'] = None
    if 'runtime_timeout' not in config_data['pywren']:
        config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_DEFAULT

    if 'storage_backend' not in config_data['pywren']:
        config_data['pywren']['storage_backend'] = 'localhost'

    if 'localhost' not in config_data:
        config_data['localhost'] = {}

    if 'workers' in config_data['pywren']:
        config_data['localhost']['workers'] = config_data['pywren']['workers']
    else:
        total_cores = multiprocessing.cpu_count()
        config_data['pywren']['workers'] = total_cores
        config_data['localhost']['workers'] = total_cores
