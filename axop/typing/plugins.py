"""
Plugins Kind
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

from typing import Literal, List, Union
from pydantic import BaseModel # pylint: disable=no-name-in-module
from .metadata import Metadata

class ConfigVariable(BaseModel): # pylint: disable=too-few-public-methods
    """Config variable model"""
    name: str
    encoding: str

class TemplateSpec(BaseModel): # pylint: disable=too-few-public-methods
    """Template Spec model"""
    payload: str
    variables: Union[List[str],List[ConfigVariable]]

class PluginSpec(BaseModel): # pylint: disable=too-few-public-methods
    """Plugin Spec model"""
    template: TemplateSpec

class PluginKind(BaseModel): # pylint: disable=too-few-public-methods
    """Plugin Kind model"""
    apiVersion: Literal['axoniq.bleuelab.ca/v1']
    kind: Literal['Plugin']
    metadata: Metadata
    spec: PluginSpec
