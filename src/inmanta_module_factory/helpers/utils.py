"""
    Copyright 2022 Inmanta

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
import re

from inmanta_module_factory.helpers.const import INMANTA_RESERVED_KEYWORDS

camel_case_regex = re.compile(r"(?<!^)(?=[A-Z])")


def camel_case_to_snake_case(input: str) -> str:
    """
    Converts a camel case string to snake case
    """
    return camel_case_regex.sub("_", input).lower()


def inmanta_entity_name(input: str) -> str:
    """
    Convert any string in a more conventional entity name.
    """
    return "".join([part.capitalize() for part in inmanta_safe_name(input).split("_")])


def inmanta_safe_name(input: str) -> str:
    """
    This helper method converts any string passed in input as a string
    that can safely be used as attribute name, relation name or module
    name.
    """
    output = input.replace("-", "_", -1).replace(".", "_", -1)
    try:
        int(output[0])
        output = f"x_{output}"
    except ValueError:
        pass

    # Attribute names can not start with a capital letter
    if output[0].upper() == output[0]:
        output = f"x_{output}"

    # Is it an inmanta keyword?
    if output in INMANTA_RESERVED_KEYWORDS:
        output = f"x_{output}"

    return output
