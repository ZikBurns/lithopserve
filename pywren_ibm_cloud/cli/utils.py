#
# (C) Copyright IBM Corp. 2020
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
import shutil
import tempfile
import logging
from pywren_ibm_cloud.config import CACHE_DIR, RUNTIMES_PREFIX, LOGS_PREFIX, \
    JOBS_PREFIX, DOCKER_PREFIX, default_config, extract_storage_config, \
    extract_compute_config
from pywren_ibm_cloud.storage import InternalStorage
from pywren_ibm_cloud.compute import Compute
from pywren_ibm_cloud.storage.utils import clean_bucket

TEMP = tempfile.gettempdir()
logger = logging.getLogger(__name__)


def clean_all(config=None):
    logger.info('Cleaning all PyWren information')
    config = default_config(config)
    storage_config = extract_storage_config(config)
    internal_storage = InternalStorage(storage_config)
    compute_config = extract_compute_config(config)
    compute_handler = Compute(compute_config)

    # Clean localhost executor temp dirs
    shutil.rmtree(os.path.join(TEMP, JOBS_PREFIX), ignore_errors=True)
    shutil.rmtree(os.path.join(TEMP, RUNTIMES_PREFIX), ignore_errors=True)
    shutil.rmtree(os.path.join(TEMP, LOGS_PREFIX), ignore_errors=True)
    shutil.rmtree(os.path.join(TEMP, DOCKER_PREFIX), ignore_errors=True)

    # Clean object storage temp dirs
    compute_handler.delete_all_runtimes()
    sh = internal_storage.storage_handler
    clean_bucket(sh, storage_config['bucket'], RUNTIMES_PREFIX, sleep=1)
    clean_bucket(sh, storage_config['bucket'], JOBS_PREFIX, sleep=1)

    # Clean local pywren cache
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
