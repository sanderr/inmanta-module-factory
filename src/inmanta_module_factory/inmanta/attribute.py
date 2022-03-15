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
from typing import Optional, Union

from typing_extensions import Literal

from inmanta_module_factory.inmanta import entity as inmanta_entity
from inmanta_module_factory.inmanta import entity_field

InmantaPrimitiveType = Literal["string", "int", "float", "number", "bool"]


class InmantaPrimitiveList:
    def __init__(self, primitive_type: InmantaPrimitiveType) -> None:
        self.primitive_type = primitive_type

    def __str__(self) -> str:
        return self.primitive_type + "[]"


InmantaAttributeType = Union[Literal["dict", "any"], InmantaPrimitiveType, InmantaPrimitiveList]


class Attribute(entity_field.EntityField):
    def __init__(
        self,
        name: str,
        inmanta_type: InmantaAttributeType,
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
        self._inmanta_type = inmanta_type
        self.optional = optional
        self.default = default
        self.description = description

    @property
    def is_list(self) -> bool:
        return isinstance(self._inmanta_type, InmantaPrimitiveList)

    @property
    def inmanta_type(self) -> str:
        return str(self._inmanta_type)

    def __str__(self) -> str:
        type_expression = self.inmanta_type
        if self.optional:
            type_expression += "?"

        default_expression = ""
        if self.default is not None:
            default_expression = f" = {self.default}"
        elif self.optional:
            default_expression = " = null"

        return f"{type_expression} {self.name}{default_expression}\n"
