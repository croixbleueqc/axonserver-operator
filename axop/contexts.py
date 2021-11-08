"""
Manages Contexts Kind
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
import kopf
import kubernetes
from . import settings
from .typing.contexts import ContextsKind, ContextsSpec, ContextSpec
from .axon.axonserver import AxonServer
from .instances import instance_from_index
from .plugins import plugin_from_index
from .utils.checks import admission_error_immutable

CONTEXTS='contexts'

def __cud_plugin(plugins_idx: kopf.Index, name: str, context: ContextSpec, # pylint: disable=too-many-arguments
    plugin: dict, axon: AxonServer, delete: bool = False):
    """
    Create, update or delete a plugin configuration for a context
    """
    plugin_instance = plugin_from_index(plugins_idx, name)
    payload = plugin_instance.get_payload(context.context, plugin)

    if delete:
        # axon.update_context_plugin_status(payload, active=False)
        axon.remove_context_plugin(payload)
    else:
        axon.update_context_plugin(payload)
        axon.update_context_plugin_status(payload, active=True)

def __cu_contexts(contexts: List[ContextSpec], axon: AxonServer, plugins_idx: kopf.Index):
    """
    Create or update contexts
    """
    for context in contexts:
        axon.update_context(context)

        if context.plugins is None:
            continue

        for name, plugin in context.plugins.items():
            __cud_plugin(plugins_idx, name, context, plugin, axon)

@kopf.on.create(settings.GROUP, settings.LATEST_VERSION, CONTEXTS, timeout=settings.DEFAULT_TIMEOUT)
def ctx_create(instances_idx: kopf.Index, plugins_idx: kopf.Index,
    body: kopf.Body, patch: kopf.Patch, **_):
    """
    Create and configure contexts
    """
    patch.status[settings.STATUS_SUCCESS] = False

    kcontexts: ContextsKind = ContextsKind.parse_obj(body)
    axon_instance = instance_from_index(instances_idx, kcontexts.spec.instance)

    with AxonServer(axon_instance) as axon:
        __cu_contexts(kcontexts.spec.contexts, axon, plugins_idx)

    patch.status[settings.STATUS_SUCCESS] = True

@kopf.on.update(settings.GROUP, settings.LATEST_VERSION, CONTEXTS, timeout=settings.DEFAULT_TIMEOUT)
def ctx_update(instances_idx: kopf.Index, plugins_idx: kopf.Index,
    body: kopf.Body, patch: kopf.Patch, old, **_):
    """
    Update contexts
    """
    patch.status[settings.STATUS_SUCCESS] = False

    kcontexts: ContextsKind = ContextsKind.parse_obj(body)
    previous = ContextsSpec(contexts=old["spec"]["contexts"], instance=old["spec"]["instance"])

    axon_instance = instance_from_index(instances_idx, kcontexts.spec.instance)

    diff_contexts = kcontexts.spec.diff_contexts(previous.contexts)

    with AxonServer(axon_instance) as axon:
        # Remove contexts
        # For reference as for now context will never been removed by the operator
        # for context in diff_contexts.removed:
        #     pass

        # Add contexts
        __cu_contexts(diff_contexts.added, axon, plugins_idx)

        # Change contexts
        for context, diff_plugins in diff_contexts.changed:
            # Remove plugins
            for name, plugin in diff_plugins.removed:
                __cud_plugin(plugins_idx, name, context, plugin, axon, delete=True)

            # Add plugins
            for name, plugin in diff_plugins.added:
                __cud_plugin(plugins_idx, name, context, plugin, axon)

            # Change plugins
            for name, plugin, old_plugin in diff_plugins.changed:
                __cud_plugin(plugins_idx, name, context, plugin, axon)

                if plugin["version"] != old_plugin["version"]:
                    # this is not the same version so we will remove the old configuration
                    __cud_plugin(plugins_idx, name, context, old_plugin, axon, delete=True)

    patch.status[settings.STATUS_SUCCESS] = True

@kopf.on.validate(settings.GROUP, settings.LATEST_VERSION, CONTEXTS)
def contextadmission(body: kopf.Body, **_):
    """
    Context Admission

    instance is immutable
    """
    if body.meta["generation"] == 1:
        return

    # previous version already exists. Checking immutable fields

    knew: ContextsKind = ContextsKind.parse_obj(body)

    with kubernetes.client.ApiClient() as api_client:
        api: kubernetes.client.CustomObjectsApi = kubernetes.client.CustomObjectsApi(api_client)
        response = api.get_namespaced_custom_object(
            settings.GROUP,
            settings.LATEST_VERSION,
            knew.metadata.namespace,
            CONTEXTS,
            knew.metadata.name
        )

    kcurrent: ContextsKind = ContextsKind.parse_obj(response)

    if kcurrent.spec.instance != knew.spec.instance:
        raise admission_error_immutable(".spec.instance")
