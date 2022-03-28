#!/usr/bin/env python3

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

"""
Packaging
"""

from pathlib import Path
from setuptools import setup, find_packages

setup(
    name='axop',
    version='0.6.3',
    python_requires='>=3.9',
    packages=find_packages(),
    install_requires=[
        'kopf',
        'certbuilder', # admission certificate for kopf
        'kubernetes',
        'pydantic',
        'requests',
        'hvac',
        'pyyaml'
    ],
    extras_require={
        "dev": [
            'kopf[dev]'
        ]
    },

    # Metadata
    author='Croix Bleue du Quebec',
    author_email='devops@qc.croixbeleue.ca',
    license='LGPL-3.0-or-later',
    description='AxonIQ Axon Server Kubernetes Operator',
    long_description_content_type='text/markdown',
    long_description=Path('README.md').read_text(encoding='UTF-8'),
    url='https://github.com/croixbleueqc/axonserver-operator',
    project_urls={
        'Bug Tracker': 'https://github.com/croixbleueqc/axonserver-operator',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
    ]
)
