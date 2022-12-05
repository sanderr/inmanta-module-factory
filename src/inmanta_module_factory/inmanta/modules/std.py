"""
    Copyright 2021 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
    Author: Inmanta
"""
from inmanta_module_factory.inmanta import (
    Attribute,
    Entity,
    Implementation,
    InmantaBooleanType,
)

entity = Entity(name="Entity", path=["std"])
none = Implementation(name="none", path=["std"], entity=entity, content="")

resource = Entity(
    name="Resource",
    path=["std"],
    fields=[
        Attribute(
            name="send_event",
            inmanta_type=InmantaBooleanType,
            default="false",
        ),
    ],
    parents=[entity],
)

purgeable_resource = Entity(
    name="PurgeableResource",
    path=["std"],
    fields=[
        Attribute(
            name="purged",
            inmanta_type=InmantaBooleanType,
            default="false",
        ),
        Attribute(
            name="purge_on_delete",
            inmanta_type=InmantaBooleanType,
            default="false",
        ),
    ],
    parents=[resource, entity],
)
