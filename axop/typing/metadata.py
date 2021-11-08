"""
Metadata definition
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

from typing import Optional
from pydantic import BaseModel # pylint: disable=no-name-in-module

class Metadata(BaseModel): # pylint: disable=too-few-public-methods
    """Kubernetes Metadata model"""
    namespace: Optional[str] # Optional for Cluster scope
    name: str
