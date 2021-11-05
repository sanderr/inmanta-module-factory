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
from typing import List, Optional, Set

from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.module_element import ModuleElement


class Implement(ModuleElement):
    def __init__(
        self,
        path: List[str],
        implementation: Implementation,
        entity: Entity,
        condition: Optional[str] = None,
        description: Optional[str] = None,
        using_parents: bool = False,
    ) -> None:
        """
        An implement statement
        :param path: The place in the module where this implem statement should be printed
        :param implementation: The implementation this statement refers to
        :param entity: The entity this statement refers to
        :param condition: A condition (inmanta boolean expression) to add to this statement
        :param description: A description to add in a docstring above the statement
        """
        super().__init__("implement", path, description)
        self.implementation = implementation
        self.entity = entity
        self.condition = condition
        self.using_parents = using_parents

    def _ordering_key(self) -> str:
        return f"{chr(255)}.implement.{self.entity.full_path_string}.{self.implementation.full_path_string}"

    def _get_derived_imports(self) -> Set[str]:
        imports = set()

        if self.path_string != self.implementation.path_string:
            # Implementation is in a different file
            imports.add(self.implementation.path_string)

        if self.path_string != self.entity.path_string:
            # Entity is in a different file
            imports.add(self.entity.path_string)

        return imports

    def validate(self) -> bool:
        # The implementation's entity should be the same as this entity or one of its parent
        if self.implementation.entity == self.entity:
            return True

        # Doing a dfs, looking into the entity's parents, and its parent's parents, etc.
        parents = [parent for parent in self.entity.parents]
        while parents:
            parent = parents.pop()
            if self.implementation.entity == parent:
                return True

            parents.extend(parent.parents)

        return False

    def __str__(self) -> str:
        entity_path = self.entity.name
        if self.path_string != self.entity.path_string:
            # Entity is in a different file
            entity_path = self.entity.full_path_string

        implementation_path = self.implementation.name
        if self.path_string != self.implementation.path_string:
            # Implementation is in a different file
            implementation_path = self.implementation.full_path_string

        if self.using_parents:
            implementation_path += ", parents"

        condition = ""
        if self.condition:
            condition = f" when {self.condition}"

        return f"implement {entity_path} using {implementation_path}{condition}\n"
