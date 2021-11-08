"""
App Kind
"""

from typing import Literal, List
from enum import Enum
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

class RolesEnum(str, Enum):
    """
    Roles supported by Axon Server
    """
    ADMIN = "ADMIN"
    CONTEXT_ADMIN = "CONTEXT_ADMIN"
    DISPATCH_COMMANDS = "DISPATCH_COMMANDS"
    DISPATCH_QUERY = "DISPATCH_QUERY"
    MONITOR = "MONITOR"
    PUBLISH_EVENTS = "PUBLISH_EVENTS"
    READ = "READ"
    READ_EVENTS = "READ_EVENTS"
    SUBSCRIBE_COMMAND_HANDLER = "SUBSCRIBE_COMMAND_HANDLER"
    SUBSCRIBE_QUERY_HANDLER = "SUBSCRIBE_QUERY_HANDLER"
    USE_CONTEXT = "USE_CONTEXT"
    WRITE = "WRITE"

class ContextSpec(BaseModel): # pylint: disable=too-few-public-methods
    """One context Spec model"""
    context: str
    roles: List[RolesEnum]

class AppSpec(BaseModel): # pylint: disable=too-few-public-methods
    """App Spec model"""
    instance: str
    description: str
    contexts: List[ContextSpec]

class AppKind(BaseModel): # pylint: disable=too-few-public-methods
    """App Kind model"""
    apiVersion: Literal['axoniq.bleuelab.ca/v1']
    kind: Literal['App']
    metadata: Metadata
    spec: AppSpec
