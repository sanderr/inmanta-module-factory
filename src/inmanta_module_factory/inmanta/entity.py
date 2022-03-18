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
from textwrap import indent
from typing import List, Optional, Sequence, Set

from inmanta_module_factory.helpers.const import INDENT_PREFIX
from inmanta_module_factory.inmanta import attribute, entity_field, entity_relation
from inmanta_module_factory.inmanta.module_element import ModuleElement


class Entity(ModuleElement):
    def __init__(
        self,
        name: str,
        path: List[str],
        fields: Optional[Sequence["entity_field.EntityField"]] = None,
        parents: Optional[Sequence["Entity"]] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        An entity definition.
        :param name: The name of the entity
        :param path: The place in the module where the entity should be printed out
        :param fields: A list of all the attributes and relations of this entity.
            All the fields provided here will be attached to this entity using their
            method `attach_entity`.
        :param parents: A list of all the entities this one inherit from
        :param description: A description of this entity, to be added in its docstring
        """
        super().__init__(name, path, description)
        self.fields = {field for field in (fields or [])}
        for field in self.fields:
            field.attach_entity(self)
        self.parents = parents or []

    def attach_field(self, field: "entity_field.EntityField") -> None:
        self.fields.add(field)

    @property
    def attributes(self) -> List["attribute.Attribute"]:
        return [field for field in self.fields if isinstance(field, attribute.Attribute)]

    @property
    def relations(self) -> List["entity_relation.EntityRelation"]:
        return [field for field in self.fields if isinstance(field, entity_relation.EntityRelation)]

    def _ordering_key(self) -> str:
        return self.name

    def _get_derived_imports(self) -> Set[str]:
        imports = set()

        for parent in self.parents:
            if self.path_string != parent.path_string:
                # Parent is in a different file
                imports.add(parent.path_string)

        return imports

    def docstring(self) -> str:
        doc = super().docstring() + "\n"

        for x_attribute in sorted(self.attributes, key=lambda x_attribute: x_attribute.name):
            description = x_attribute.description or ""
            doc += f":attr {x_attribute.name}: {description}\n"

        for relation in sorted(self.relations, key=lambda relation: relation.name):
            if not relation.name:
                # Skipping one-direction relations on the side where they are not defined
                continue

            description = relation.description or ""
            doc += f":rel {relation.name}: {description}\n"

        return doc

    def _definition(self) -> str:
        inheritance = ""
        if self.parents:
            parents = []
            for parent in self.parents:
                parent_path = parent.name
                if self.path_string != parent.path_string:
                    # Parent is in a different file
                    parent_path = parent.full_path_string

                parents.append(parent_path)

            inheritance = " extends " + ", ".join(parents)

        return f"entity {self.name}{inheritance}:\n"

    def __str__(self) -> str:
        return (
            self._definition()
            + indent(
                (
                    '"""\n'
                    + self.docstring()
                    + '"""\n'
                    + "".join([str(attribute) for attribute in sorted(self.attributes, key=lambda attr: attr.name)])
                ),
                prefix=INDENT_PREFIX,
            )
            + "end\n"
        )
