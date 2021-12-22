"""
AxonIQ Server EE
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

from typing import List
import requests
from .errors import ErrAxonServerNetwork
from ..instances import InternalInstance
from ..typing.contexts import ContextSpec
from ..typing.apps import AppSpec

class AxonServer():
    """AxonIQ Server EE"""

    def __init__(self, instance: InternalInstance):
        self._instance = instance
        self._session = None

    @property
    def url(self) -> str:
        """Axon Server API endpoint"""
        return self._instance.http

    @property
    def headers(self) -> dict:
        """Axon Server API headers"""
        return {
            "AxonIQ-Access-Token": self._instance.get_axon_token()
        }

    @property
    def session(self) -> requests.Session:
        """Network session with Axon Server"""
        return self._session

    def __enter__(self):
        self._session = requests.session()
        self._session.headers.update(self.headers)
        return self

    def __exit__(self, type, value, traceback): # pylint: disable=redefined-builtin
        self._session.close()
        self._session = None

    @classmethod
    def _check(cls, response: requests.Response, status_accepted: List[int]):
        if response.status_code not in status_accepted:
            raise ErrAxonServerNetwork(response.status_code, response.text)

    def update_context(self, context: ContextSpec):
        """Create/update multiple contexts"""

        response = self.session.post(
            f"{self.url}/v1/context",
            json = {
                "context": context.context,
                "replicationGroup": context.replicationGroup
            }
        )

        # since 4.5.11, post with an existing context will result in:
        # code: 400 - message: [AXONIQ-1304] Context already exists
        if response.status_code == 400 and "[AXONIQ-1304]" in response.text:
            return

        self._check(response, [200])

    def update_context_plugin(self, payload: dict):
        """Update plugin configuration"""

        response = self.session.post(f"{self.url}/v1/plugins/configuration", json=payload)
        self._check(response, [200, 201])

    def update_context_plugin_status(self, payload: dict, active: bool=True):
        """Enable/Disable a plugin"""

        name = payload["name"]
        context = payload["context"]
        version = payload["version"]

        response = self.session.post(
            f"{self.url}/v1/plugins/status?active={active}" \
            f"&name={name}" \
            f"&targetContext={context}" \
            f"&version={version}"
        )
        self._check(response, [200, 201])

    def remove_context_plugin(self, payload: dict):
        """Remove plugin configuration for the context"""

        name = payload["name"]
        context = payload["context"]
        version = payload["version"]

        response = self.session.delete(
            f"{self.url}/v1/plugins/context?" \
            f"name={name}" \
            f"&targetContext={context}" \
            f"&version={version}"
        )
        self._check(response, [200, 204])

    def update_application(self, uid: str, app: AppSpec) -> str:
        """Register/Update an application with contexts roles"""

        payload = {
            "name": uid,
            "description": app.description,
            "roles": [i.dict() for i in app.contexts]
        }

        response = self.session.post(f"{self.url}/v1/applications", json=payload)
        self._check(response, [200])

        return response.text

    def unregister_application(self, uid: str):
        """Unregister an application"""

        response = self.session.delete(f"{self.url}/v1/applications/{uid}")
        self._check(response, [200, 404])
