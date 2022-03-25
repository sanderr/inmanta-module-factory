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
from typing import Literal


class InmantaType:
    """
    Base class for all inmanta attribute type representations.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def path_string(self) -> str:
        """
        This methods can be used to differentiate typedefs from primitive types
        A primitive type will always have an empty path_string as it is not defined anywhere
        in our model.
        """
        return ""

    @property
    def full_path_string(self) -> str:
        """
        This methods can be used to differentiate typedefs from primitive types
        A primitive type will always have as full_path_string its name as it has not been defined
        anywhere in our model.
        """
        return self.name

    def __str__(self) -> str:
        return self.name


class InmantaAdvancedType(InmantaType, str):
    """
    This class represents all inmanta primitive types that can not be used as base type typedefs or lists
    """

    def __init__(self, name: Literal["dict", "any"]) -> None:
        super().__init__(name)


InmantaDictType = InmantaAdvancedType("dict")
InmantaAnyType = InmantaAdvancedType("any")


class InmantaBaseType(InmantaType):
    """
    This class represents all inmanta types that can be used a base type for typedefs or lists
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)


class InmantaPrimitiveType(InmantaBaseType, str):
    """
    This class represents all the inmanta primitive types that can be used as base type for typedefs
    or lists
    """

    def __init__(self, name: Literal["int", "bool", "number", "string"]) -> None:
        super().__init__(name)


InmantaIntegerType = InmantaPrimitiveType("int")
InmantaBooleanType = InmantaPrimitiveType("bool")
InmantaNumberType = InmantaPrimitiveType("number")
InmantaStringType = InmantaPrimitiveType("string")


class InmantaListType(InmantaType):
    """
    This class represents all list types in inmanta language, a list type is composed of a base type, which
    is the type of each item of the list.
    """

    def __init__(self, item_type: InmantaBaseType) -> None:
        super().__init__(item_type.name + "[]")
        self.item_type = item_type

    @property
    def path_string(self) -> str:
        """
        The path_string of a list is the same one as the one of its item type
        """
        return self.item_type.path_string

    @property
    def full_path_string(self) -> str:
        """
        The full_path_string of a list is the same one as the one of its item type plus "[]"
        """
        return self.item_type.full_path_string + "[]"
