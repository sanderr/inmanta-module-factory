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
from typing import Dict

from pydantic import BaseModel


class ModuleFileStats(BaseModel):
    entity_count: int = 0
    """
    The amount of entities that will be created in the file
    """

    entity_relation_count: int = 0
    """
    The amount of entity relations that will be created in the file
    """

    index_count: int = 0
    """
    The amount of index statements that will be created in the file
    """

    implement_count: int = 0
    """
    The amount of implement statements that will be created in the file
    """

    implementation_count: int = 0
    """
    The amount of implementation code blocks that will be created in the file
    """

    type_def_count: int = 0
    """
    The amount of type definitions that will be added in the file
    """


class ModuleStats(ModuleFileStats):
    """
    The stats inherited from the base class are the sum of the stats in the module_init_stats
    and all the sub_modules_stats.
    """

    module_init_stats: ModuleFileStats
    """
    Stats about the _init.cf file at the root of this module
    """

    sub_modules_stats: Dict[str, "ModuleStats"]
    """
    Stats about all the sub modules of this module
    """
