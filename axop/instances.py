"""
Manages Instances kind
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

import kopf
from . import settings
from .typing.instances import InstancesKind
from .secrets.vault import HashiCorpVault

INSTANCES='instances'

class InternalInstance():
    """
    Internal Instance
    """
    def __init__(self, kinstance: InstancesKind):
        self._kinstance = kinstance
        self._axon_token = None

    @property
    def http(self) -> str:
        """Axon API endpoint"""
        return self._kinstance.spec.http

    @property
    def grpc(self) -> str:
        """Axon GRPC endpoints"""
        return self._kinstance.spec.grpc

    def get_axon_token(self) -> str:
        """
        Return the Axon token associated with the instance
        """
        if self._axon_token is not None:
            return self._axon_token

        if self._kinstance.spec.token.hashicorpVault is not None:
            # get token from vault
            spec = self._kinstance.spec.token.hashicorpVault

            self._axon_token = HashiCorpVault.get_one_secret(spec)
            return self._axon_token

        raise ValueError("Axon token is not available !")

@kopf.index(settings.GROUP, settings.LATEST_VERSION, INSTANCES)
def instances_idx(body: kopf.Body, **_):
    """
    Index all instances
    """
    kinstance: InstancesKind = InstancesKind.parse_obj(body)

    return {
        kinstance.metadata.name: InternalInstance(kinstance)
    }

def instance_from_index(index: kopf.Index, name: str) -> InternalInstance:
    """
    Get internal instance from Index or raise a temporary error
    """
    instances = index.get(name, [])

    if isinstance(instances, kopf.Store) and len(instances) > 0:
        instance = list(instances)[-1]
    else:
        instance = None

    if instance is None:
        raise kopf.TemporaryError(f"instance {name} is not available in index")

    return instance
