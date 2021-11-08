"""
Exceptions class for Axon Server
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

class AxonBrokerException(Exception):
    """Generic Axon Exception"""

class ErrAxonServerNetwork(AxonBrokerException):
    """Network Issue"""
    def __init__(self, status_code: int, msg: str):
        AxonBrokerException.__init__(self,
            f"Network error occured. status_code={status_code}, msg={msg}")
