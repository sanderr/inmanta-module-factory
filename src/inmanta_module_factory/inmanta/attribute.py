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
from inmanta_module_factory.inmanta import entity_field
from inmanta_module_factory.inmanta.types import InmantaType


class Attribute(entity_field.EntityField):
    def __init__(
        self,
        name: str,
        inmanta_type: InmantaType,
        optional: bool = False,
        default: Optional[str] = None,
        description: Optional[str] = None,
        entity: Optional["inmanta_entity.Entity"] = None,
    ) -> None:
        """
        :param name: The name of the attribute
        :param inmanta_type: The type of the attribute
        :param optional: Whether this attribute is optional or not
        :param default: Whether this attribute has a default value or not
        :param description: A description of the attribute to add in the docstring
        :param entity: The entity this attribute is a part of
        """
        entity_field.EntityField.__init__(self, name, entity)
        self.inmanta_type = inmanta_type
        self.optional = optional
        self.default = default
        self.description = description

    @property
    def is_list(self) -> bool:
        return str(self.inmanta_type).endswith("[]")

    def __str__(self) -> str:
        # The type reference is the full path if the type is not defined
        # in the same file as this typedef
        type_expression = (
            self.inmanta_type.full_path_string
            if self.inmanta_type.path_string != self.entity.path_string
            else self.inmanta_type.name
        )

        if self.optional:
            type_expression += "?"

        default_expression = ""
        if self.default is not None:
            default_expression = f" = {self.default}"
        elif self.optional:
            default_expression = " = null"

        return f"{type_expression} {self.name}{default_expression}\n"
