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
from typing import List, Optional, Set

from inmanta_module_factory.helpers.const import INDENT_PREFIX
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.module_element import ModuleElement


class Implementation(ModuleElement):
    def __init__(
        self,
        name: str,
        path: List[str],
        entity: Entity,
        content: str,
        description: Optional[str] = None,
    ) -> None:
        """
        An implementation statement.
        :param name: The name of this implementation
        :param path: The place in the module where the implementation should be printed
        :param entity: The entity this implementation belongs to
        :param content: The content (inmanta statements) of the implementation
        :param description: A description of the implementation, to be added as docstring
        """
        super().__init__(name, path, description)
        self.entity = entity
        self.content = content

    def _ordering_key(self) -> str:
        return f"{chr(255)}.implementation.{self.name}"

    def _get_derived_imports(self) -> Set[str]:
        imports = set()

        if self.path_string != self.entity.path_string:
            # Entity is in a different file
            imports.add(self.entity.path_string)

        return imports

    def __str__(self) -> str:
        entity_path = self.entity.name
        if self.path_string != self.entity.path_string:
            # Entity is in a different file
            entity_path = self.entity.full_path_string

        return (
            f"implementation {self.name} for {entity_path}:\n" + indent(self.content.strip(), prefix=INDENT_PREFIX) + "\nend\n"
        )
