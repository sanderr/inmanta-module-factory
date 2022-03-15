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
from typing import Optional

from inmanta_module_factory.inmanta import entity as inmanta_entity


class EntityField:
    def __init__(self, name: str, entity: Optional["inmanta_entity.Entity"] = None) -> None:
        """
        A base class for the entity attributes and relations
        :param name: The name of the class field
        :param entity: The entity this field is a member of
            If the entity is provided here, the field will be automatically attached to the
            entity as well.  If you don't provide the entity here, the method `attach_entity`
            has to be called later on.  The constructor of `Entity` calls this method
            automatically.
        """
        self.name: str = name
        self._entity = entity
        if self._entity is not None:
            self._entity.attach_field(self)

    @property
    def entity(self) -> "inmanta_entity.Entity":
        assert self._entity is not None
        return self._entity

    def attach_entity(self, entity: "inmanta_entity.Entity") -> None:
        self._entity = entity
