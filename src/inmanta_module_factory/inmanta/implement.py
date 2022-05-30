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
from typing import List, Optional, Sequence, Set

from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.module_element import ModuleElement


class Implement(ModuleElement):
    def __init__(
        self,
        path: List[str],
        implementation: Optional[Implementation],
        entity: Entity,
        condition: Optional[str] = None,
        description: Optional[str] = None,
        using_parents: bool = False,
        *,
        implementations: Optional[Sequence[Implementation]] = None,
    ) -> None:
        """
        An implement statement
        :param path: The place in the module where this implem statement should be printed
        :param implementation: (deprecated) The implementation this statement refers to
        :param entity: The entity this statement refers to
        :param condition: A condition (inmanta boolean expression) to add to this statement
        :param description: A description to add in a docstring above the statement
        """
        super().__init__(
            f"{'+'.join([i.name for i in implementations or []])}, using_parents={using_parents}",
            path,
            description,
        )

        if implementation is not None and implementations:
            raise ValueError("Parameter implementation and implementations can not be used together")
        elif implementation is not None:
            self._logger.warning("The implementation argument is deprecated, use implementations instead")
            self.implementations = [implementation]
        else:
            self.implementations = list(implementations or [])

        self.entity = entity
        self.condition = condition
        self.using_parents = using_parents

    @property
    def implementation(self) -> Implementation:
        self._logger.warning("Usage of implementation is deprecated, use implementations instead")
        return self.implementations[0]

    def _ordering_key(self) -> str:
        implementations_key = ".".join(implementation.full_path_string for implementation in self.implementations)
        return f"{chr(255)}.implement.{self.entity.full_path_string}.{implementations_key}"

    def _get_derived_imports(self) -> Set[str]:
        imports = set()

        for implementation in self.implementations:
            if self.path_string != implementation.path_string:
                # Implementation is in a different file
                imports.add(implementation.path_string)

        if self.path_string != self.entity.path_string:
            # Entity is in a different file
            imports.add(self.entity.path_string)

        return imports

    def _validate_implementation(self, implementation: Implementation) -> bool:
        # The implementation's entity should be the same as this entity or one of its parent
        if implementation.entity == self.entity:
            return True

        # Doing a dfs, looking into the entity's parents, and its parent's parents, etc.
        parents = [parent for parent in self.entity.parents]
        while parents:
            parent = parents.pop()
            if implementation.entity == parent:
                return True

            parents.extend(parent.parents)

        self._logger.warning(f"Failed to validate for {implementation.name}")
        return False

    def validate(self) -> bool:
        if not self.implementations and not self.using_parents:
            # We need to have at least one implementations
            # or using_parents must be True, otherwise this implement
            # statement is useless (and incomplete)
            self._logger.warning(
                "Every implement statement should reference at least one implementation or " "have using_parents set to True"
            )
            return False

        return all(self._validate_implementation(implementation) for implementation in self.implementations)

    def __str__(self) -> str:
        entity_path = self.entity.name
        if self.path_string != self.entity.path_string:
            # Entity is in a different file
            entity_path = self.entity.full_path_string

        implementation_paths: List[str] = []
        for implementation in self.implementations:
            implementation_path = implementation.name
            if self.path_string != implementation.path_string:
                # Implementation is in a different file
                implementation_path = implementation.full_path_string
            implementation_paths.append(implementation_path)

        if self.using_parents:
            implementation_paths.append("parents")

        condition = ""
        if self.condition:
            condition = f" when {self.condition}"

        docstring = self.docstring()
        if docstring:
            docstring = f'"""\n{docstring}\n"""'

        return f"implement {entity_path} using {', '.join(implementation_paths)}{condition}\n{docstring}"
