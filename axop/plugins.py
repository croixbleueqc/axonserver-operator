"""
Manages Plugin kind
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
import yaml
from . import settings
from .typing.plugins import PluginKind
from .secrets.vault import unravel_mysteries

PLUGINS='plugins'

class InternalPlugin(): # pylint: disable=too-few-public-methods
    """
    Internal Plugin
    """
    def __init__(self, kplugin: PluginKind):
        self._kplugin = kplugin

    def get_payload(self, context: str, plugin: dict) -> dict:
        """
        Replace required fields in the payload
        """
        required = self._kplugin.spec.template.variables
        values = {}

        for i in required:
            if i == "context":
                values["context"] = context
                continue
            values[i] = plugin[i]

        payload = yaml.safe_load(
            self._kplugin.spec.template.payload.format(**values)
        )

        unravel_mysteries(payload)

        return payload

@kopf.index(settings.GROUP, settings.LATEST_VERSION, PLUGINS)
def plugins_idx(body: kopf.Body, **_):
    """
    Index all plugins
    """
    kplugin: PluginKind = PluginKind.parse_obj(body)

    return {
        kplugin.metadata.name: InternalPlugin(kplugin)
    }

def plugin_from_index(index: kopf.Index, name: str) -> InternalPlugin:
    """
    Get internal plugin from Index or raise a temporary error
    """
    plugins = index.get(name, [])

    if isinstance(plugins, kopf.Store) and len(plugins) > 0:
        plugin = list(plugins)[-1]
    else:
        plugin = None

    if plugin is None:
        raise kopf.TemporaryError(f"plugin {name} is not available in index")

    return plugin
