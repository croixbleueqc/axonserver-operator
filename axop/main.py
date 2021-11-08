"""
Internal Startup/Shutdown/...
"""

# Copyright 2021 Croix Bleue du Québec

# This file is part of axop.

# axop is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# axop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with axop.  If not, see <https://www.gnu.org/licenses/>.

import logging
import re
import os
import random
from typing import AsyncIterator
import kopf
from . import settings as axop_settings

class FilterAccessLogger(logging.Filter): # pylint: disable=too-few-public-methods
    """
    /health filter

    Hidding those requests if we have a 200 OK when we are not in DEBUG
    """
    regex = re.compile(r'.*"GET /healthz HTTP\/\d.\d" 200 ')

    def filter(self, record: logging.LogRecord):
        if record.levelno == logging.DEBUG:
            return True

        if FilterAccessLogger.regex.match(record.getMessage()) is not None:
            # match GET /healthz with code 200
            return False

        return True

aiohttp_access = logging.getLogger("aiohttp.access")
aiohttp_access.addFilter(FilterAccessLogger())

class K8sWebhook(kopf.WebhookServer):
    """
    Kubernetes Webhook with service definition in config (replace regular url)

    workaround DNS issue (no such host) when using .svc.cluster.local url
    """
    regex = re.compile(r'.*://([\w-]*)\.([\w-]*).svc:(\d*)')

    async def __call__(self, fn: kopf.WebhookFn) -> AsyncIterator[kopf.WebhookClientConfig]:
        async for client_config in kopf.WebhookServer.__call__(self, fn):
            # adjust the config
            config = K8sWebhook.regex.match(client_config["url"])

            if config is None:
                logging.warning(
                    "Can not convert the url '%s' to a service definition",
                    client_config["url"]
                )
            else:
                client_config["service"] = kopf.WebhookClientConfigService(
                    name = config.group(1),
                    namespace = config.group(2),
                    port = int(config.group(3))
                )
                client_config["url"] = None

            yield client_config

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    """
    startup
    """
    # watching
    settings.watching.server_timeout = axop_settings.WATCHING_SERVER_TIMEOUT
    settings.watching.connect_timeout = axop_settings.WATCHING_CONNECT_TIMEOUT

    # peering
    settings.peering.priority = random.randint(0, 32767)
    # settings.peering.stealth = True

    # Admission
    host = os.environ.get(axop_settings.ENV_HOST)
    if host is not None:
        settings.admission.server = \
            K8sWebhook(addr='0.0.0.0', port=5001, host=host, extra_sans=[host])
    else:
        settings.admission.server = kopf.WebhookAutoServer(addr='0.0.0.0', port=5001)
    settings.admission.managed = axop_settings.DEFAULT_ADMISSION_MANAGED

    # Storage
    settings.persistence.finalizer = f'{axop_settings.DOMAIN}/kopf-finalizer'
    settings.persistence.progress_storage = kopf.StatusProgressStorage(name=axop_settings.OPERATOR)
    settings.persistence.diffbase_storage = kopf.AnnotationsDiffBaseStorage(
        prefix=axop_settings.DOMAIN,
        key='last-handled-configuration',
    )
