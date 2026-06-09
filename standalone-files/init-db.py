# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import sys
import logging
from univention.ox.provisioning.db import initialize_db

logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger('init-db')

try:
    initialize_db()
    logger.info('Database initialization completed successfully')
    sys.exit(0)
except Exception as e:
    logger.exception('Database initialization failed: %s', e)
    sys.exit(1)
