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
from typing import List, Optional, Set, Tuple

from inmanta_module_factory.inmanta import entity as inmanta_entity
from inmanta_module_factory.inmanta import entity_field
from inmanta_module_factory.inmanta.module_element import ModuleElement


class EntityRelation(entity_field.EntityField, ModuleElement):
    def __init__(
        self,
        name: str,
        path: List[str],
        cardinality: Tuple[int, Optional[int]],
        description: Optional[str] = None,
        peer: Optional["EntityRelation"] = None,
        entity: Optional["inmanta_entity.Entity"] = None,
    ) -> None:
        """
        A relation statement (or rather half of it).
        :param name: The name of the relation
        :param path: The path in the module where the relation should be printed
        :param cardinality: The multiplicity of the relation, a tuple contianing the min and max
        :param description: A description of the relation
        :param peer: The peer relation, which goes on the other end of "--"
        :param entity: The entity this relations belongs to
        """
        entity_field.EntityField.__init__(self, name, entity)
        ModuleElement.__init__(self, name, path, description)
        self._peer = peer
        if self._peer is not None:
            self._peer._peer = self

        self.cardinality_min = str(cardinality[0])
        self.cardinality_max = str(cardinality[1] or "")
        self._is_single = (cardinality[1] or 2) == 1

    def _ordering_key(self) -> str:
        if self.path_string != self.entity.path_string:
            return f"{chr(255)}.relation.{self.entity.full_path_string}_{self.name}"

        return f"{self.entity.ordering_key}.{self.name}"

    @property
    def is_single(self) -> bool:
        return self._is_single

    @property
    def peer(self) -> "EntityRelation":
        if self._peer is None:
            raise RuntimeError(f"This entity relation doesn't have any peer: {self.name} on {self.entity.name}")

        return self._peer

    def _raise_if_not_complete(self) -> None:
        if not self.name:
            raise RuntimeError("The relation attribute can not be empty on the left side")

    def _get_derived_imports(self) -> Set[str]:
        imports = set()

        if self.path_string != self.entity.path_string:
            # Entity is in another file
            imports.add(self.entity.path_string)

        if self.path_string != self.peer.entity.path_string:
            # Peer entity is in another file
            imports.add(self.peer.entity.path_string)

        return imports

    def __str__(self) -> str:
        self._raise_if_not_complete()

        entity_path = self.entity.name
        if self.path_string != self.entity.path_string:
            # Entity is in another file
            entity_path = self.entity.full_path_string

        peer_entity_path = self.peer.entity.name
        if self.path_string != self.peer.entity.path_string:
            # Peer entity is in another file
            peer_entity_path = self.peer.entity.full_path_string

        cardinality = f"[{self.cardinality_min}:{self.cardinality_max}]"
        if self.cardinality_min == self.cardinality_max:
            cardinality = f"[{self.cardinality_min}]"

        peer_suffix = f".{self.peer.name} [{self.peer.cardinality_min}:{self.peer.cardinality_max}]"
        if not self.peer.name:
            peer_suffix = ""
        elif self.peer.cardinality_min == self.peer.cardinality_max:
            peer_suffix = f".{self.peer.name} [{self.peer.cardinality_min}]"

        docstring = self.docstring()
        if docstring:
            docstring = f'"""\n{docstring}\n"""\n'

        return f"{entity_path}.{self.name} {cardinality} -- {peer_entity_path}{peer_suffix}\n{docstring}"
