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
from abc import abstractmethod
from typing import List, Optional, Set


class ModuleElement:
    def __init__(self, name: str, path: List[str], description: Optional[str] = None) -> None:
        """
        A module element is any Inmanta language component with a specific role and syntax.

        :param name: The name of such element.  The name of the entity if it is an entity, of the
            implementation if it is an implementation etc.
        :param path: The path where this element should be located in its module.  The first element
            should match the name of the module, and would place the entity in model/_init.cf.  Every
            additional item in the path will take the component one folder deaper.
        :param description: And optional description, that will be printed in some docstring next to
            the element.
        """
        self.name = name
        self.path = path
        self.description = description
        self.imports: Set[str] = set()
        self._forced_ordering_key: Optional[str] = None

        if not path:
            raise ValueError(
                "The length of the path should be at least one but the list is empty.  "
                "The first element should be the name of the module."
            )

    @abstractmethod
    def _ordering_key(self) -> str:
        """
        This value will be used to order elements in the same file.
        """
        pass

    @property
    def ordering_key(self) -> str:
        """
        This value will be used to order elements in the same file.
        """
        if self._forced_ordering_key is not None:
            return self._forced_ordering_key

        return self._ordering_key()

    def overwrite_ordering_key(self, key: str) -> None:
        """
        Overwrite the default ordering key picked by the entity with this one.
        """
        self._forced_ordering_key = key

    def docstring(self) -> str:
        description = ""
        if self.description:
            description = self.description + "\n"
        return "This docstring has been automatically generated.\n" + description

    def validate(self) -> bool:
        """
        This method will be called for each entity before generating the module, some check
        over the validity of the input can be done in it.
        """
        return True

    @abstractmethod
    def _get_derived_imports(self) -> Set[str]:
        """
        This method should be implemented by the children classes, it should return a set containing
        all the derived imports for this specific element.
        """
        pass

    def get_imports(self) -> Set[str]:
        """
        A list of import values that this element requires.
        """
        return self._get_derived_imports() | self.imports

    def add_import(self, import_value: str) -> None:
        """
        Add an import that this element requires.  This is required if the import requirement can
        not be derived from the arguments of the constructor of the object.
        ex: For an implementation, the import path of the entity can be automatically derived.  But
            any usage of a foreign (with respect to the file) entity inside of the file will require
            and import to be added using this method.
        """
        self.imports.add(import_value)

    @property
    def path_string(self) -> str:
        """
        This returns the path of this entity's file in this module.  The name of the module
        is the first element of the path.
        """
        return "::".join(self.path)

    @property
    def full_path_string(self) -> str:
        """
        This returns the path of this entity in this module.  The difference with path_string
        is that this one contains the name of the entity at the end.
        """
        return "::".join(self.path + [self.name])

    def __str__(self) -> str:
        raise NotImplementedError("A module element is not part of the inmanta syntax.")


class DummyModuleElement(ModuleElement):
    def __init__(self, path: List[str]) -> None:
        super().__init__("dummy", path, description=None)

    def _ordering_key(self) -> str:
        return ""

    def _get_derived_imports(self) -> Set[str]:
        return set()

    def __str__(self) -> str:
        return ""
