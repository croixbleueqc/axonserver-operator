"""
Vault Helper

env:
- VAULT_ADDR: Vault address
- VAULT_TOKEN: Token for the account
- VAULT_ROLE: Role used to login
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

import os
import logging
from typing import Optional, Any, Dict
from pathlib import Path
import hvac
from . import VaultGenericException
from ..typing.vault import HashiCorpVaultSpec

# class ListworkaroundRequest(hvac.adapters.Request):
#     """workaround for an HTTP/2 issue with LIST/istio/vault on kubernetes"""

#     def request(self, method, url, headers=None, raise_exception=True, **kwargs):
#         """override request function to change the LIST method to a GET one"""

#         if method == "list":
#             method = "get"
#             url = url + "?list=true"

#         return hvac.adapters.Request.request(
#             self, method, url, headers=headers, raise_exception=raise_exception, **kwargs)

vault_logger = logging.getLogger("axop.vault")

class HashiCorpVault:
    """Vault helper

    Purpose is to find the proper context to connect to the vault and to provide read functions.
    """

    @classmethod
    def get_one_secret(cls, spec: HashiCorpVaultSpec) -> Any:
        """
        Initialize the vault and return the secret requested (All-in-one)
        """
        vault = HashiCorpVault(spec.auth, spec.addr, spec.role)
        vault.connect()
        result = vault.read_secret(spec.path, spec.mount)

        return result[spec.field]

    def __init__(self, auth: str = "kubernetes",
        addr: str = "http://localhost:8200", role: str = "default"):
        self._k8s = False
        self._k8s_auth = auth
        self._token = None
        self._client = None

        self._addr = os.environ.get("VAULT_ADDR", addr)
        self._role = os.environ.get("VAULT_ROLE", role)

        vault_logger.debug("VAULT_ADDR: %s", self._addr)
        vault_logger.debug("VAULT_ROLE: %s", self._role)

        try:
            self._token = self._get_token_from_kubernetes()
            self._k8s = True
            vault_logger.debug("Token set from kubernetes [auth: %s].", self._k8s_auth)
            return
        except FileNotFoundError:
            pass

        try:
            self._token = self._get_token_from_env()
            vault_logger.debug("Token set from env.")
            return
        except KeyError:
            pass

    def connect(self):
        """Connect to the Vault"""
        # client = hvac.Client(url=self._addr, adapter=ListworkaroundRequest)
        client = hvac.Client(url=self._addr)

        if self._k8s:
            # Deprecated but not well documented so we keep it as a reference for now
            # client.auth_kubernetes(self._role, self._token, mount_point=self._k8s_auth)
            client.auth.kubernetes.login(self._role, self._token, mount_point=self._k8s_auth)
        elif self._token is not None:
            client.token = self._token
        if not client.is_authenticated():
            raise VaultGenericException(f"Auth failure on {self._addr} !")

        self._client = client
        vault_logger.info("Auth succeed on %s", self._addr)

    @classmethod
    def _get_token_from_kubernetes(cls):
        """Get the service account token from a Pod"""
        return Path('/var/run/secrets/kubernetes.io/serviceaccount/token') \
                .read_text(encoding='UTF-8')

    @classmethod
    def _get_token_from_env(cls):
        """Get a token set in environment variables"""
        return os.environ["VAULT_TOKEN"]

    def assert_valid_client(self):
        """
        Check if vault client has been initialized
        """
        if self._client is None:
            raise VaultGenericException(f"Not connected to {self._addr} !")

    def read_secret(self, path: str, mount_point: str = "secret") -> Optional[dict]:
        """Read a secret"""

        self.assert_valid_client()

        response = self._client.secrets.kv.v2.read_secret_version(path, mount_point=mount_point)
        return response['data']['data']

def unravel_mysteries(var: dict, vault_key: str='hashicorpVault'):
    """
    Find hashicorpVault key compliant with HashiCorpVaultSpec
    and replace the previous key with the secret value

    eg:
    azureServicePrincipalSecret:
      hashicorpVault:
        addr: ''
        role: ''
        auth: ''
        path: ''
        mount: ''
        field: ''

    will become:
    azureServicePrincipalSecret: 'mysecret'
    """
    _vault_cache: Dict[str, HashiCorpVault] = {}

    def lookin(var: dict):
        for key, value in var.items():
            if isinstance(value, dict):
                if vault_key in value:
                    spec: HashiCorpVaultSpec = HashiCorpVaultSpec.parse_obj(value[vault_key])
                    vault = _vault_cache.get(spec.addr)
                    if vault is None:
                        vault = HashiCorpVault(spec.auth, spec.addr, spec.role)
                        vault.connect()
                        _vault_cache[spec.addr] = vault

                    var[key] = vault.read_secret(spec.path, spec.mount)[spec.field]
                else:
                    lookin(value)

    lookin(var)
