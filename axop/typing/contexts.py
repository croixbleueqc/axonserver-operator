"""
Contexts Kind
"""

from typing import Literal, List, Optional, Tuple, Dict
from pydantic import BaseModel # pylint: disable=no-name-in-module
from .metadata import Metadata

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

class PluginsDiff(BaseModel): # pylint: disable=too-few-public-methods
    """Diff between plugins"""
    removed: List[Tuple[str, dict]]
    added: List[Tuple[str, dict]]
    changed: List[Tuple[str, dict, dict]]

    def empty(self) -> bool:
        """Check if there is no diff"""
        return len(self.removed) == len(self.added) == len(self.changed) == 0

class ContextSpec(BaseModel): # pylint: disable=too-few-public-methods
    """One context Spec model"""
    context: str
    replicationGroup: str = 'default'
    plugins: Optional[dict]

    def diff_plugins(self, previous: Optional[dict]) -> PluginsDiff:
        """Difference between 2 plugins"""

        # Create sets of keys only
        previous_keys = set(previous or {})
        current_keys = set(self.plugins or {})

        removed = list(map(lambda x: (x, previous[x]), list(previous_keys - current_keys)))
        added = list(map(lambda x: (x, self.plugins[x]), list(current_keys - previous_keys)))

        changed = []
        for name in list(current_keys & previous_keys):
            if self.plugins[name] != previous[name]:
                changed.append((name, self.plugins[name], previous[name]))

        return PluginsDiff(
            removed = removed,
            added = added,
            changed = changed
        )

class ContextsDiff(BaseModel): # pylint: disable=too-few-public-methods
    """Diff between contexts"""
    removed: List[ContextSpec]
    added: List[ContextSpec]
    changed: List[Tuple[ContextSpec, PluginsDiff]]

    def empty(self) -> bool:
        """Check if there is no diff"""
        return len(self.removed) == len(self.added) == len(self.changed) == 0

class ContextsSpec(BaseModel): # pylint: disable=too-few-public-methods
    """Contexts Spec model"""
    instance: str
    contexts: List[ContextSpec]

    def diff_contexts(self, previous: List[ContextSpec]) -> ContextsDiff:
        """Difference between 2 contexts"""

        # Create dicts where key is the context name (list to dict)
        current_dict: Dict[str, ContextSpec] = dict(map(lambda x: (x.context, x), self.contexts))
        previous_dict: Dict[str, ContextSpec] = dict(map(lambda x: (x.context, x), previous))

        # Create sets of keys only
        previous_keys = set(previous_dict)
        current_keys = set(current_dict)

        removed = list(map(lambda x: previous_dict[x], list(previous_keys - current_keys)))
        added = list(map(lambda x: current_dict[x], list(current_keys - previous_keys)))

        changed = []
        for context in list(current_keys & previous_keys):
            diff = current_dict[context].diff_plugins(previous_dict[context].plugins)
            if not diff.empty():
                changed.append((current_dict[context], diff))

        return ContextsDiff(
            removed = removed,
            added = added,
            changed = changed
        )

class ContextsKind(BaseModel): # pylint: disable=too-few-public-methods
    """Contexts Kind model"""
    apiVersion: Literal['axoniq.bleuelab.ca/v1']
    kind: Literal['Context']
    metadata: Metadata
    spec: ContextsSpec
