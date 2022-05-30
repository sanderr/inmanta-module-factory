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
import shutil
from pathlib import Path

import pytest
from pytest_inmanta.plugin import Project

from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.inmanta.attribute import Attribute
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.implement import Implement
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.module import Module
from inmanta_module_factory.inmanta.types import InmantaListType, InmantaStringType


def test_multiple_implementations(project: Project) -> None:
    """
    This simple test creates a more complex module, with entities, implementations, index, etc.
    It then validates that the modules can be compiled and that its entities can be used.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module)

    entity = Entity(
        "Test",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type=InmantaListType(InmantaStringType),
                default="[]",
                description="This is a test list attribute",
            ),
        ],
        description="This is a test entity",
    )

    index_attribute = Attribute(
        name="test1",
        inmanta_type=InmantaStringType,
        description="This is a test attribute",
        entity=entity,
    )

    implementation_1 = Implementation(
        name="test1",
        path=[module.name],
        entity=entity,
        content=f"std::print(self.{index_attribute.name})",
        description="This is a test implementation",
    )

    implementation_2 = Implementation(
        name="test2",
        path=[module.name],
        entity=entity,
        content=f"std::print(self.{index_attribute.name})",
        description="This is another test implementation",
    )

    implement = Implement(
        path=[module.name],
        implementation=None,
        entity=entity,
        implementations=[implementation_1, implementation_2],
    )

    module_builder.add_module_element(entity)
    module_builder.add_module_element(implementation_1)
    module_builder.add_module_element(implementation_2)
    module_builder.add_module_element(implement)

    module_builder.generate_module(Path(project._test_project_dir) / "libs")

    project.compile(
        """
            import test

            test::Test(
                test1="a",
            )
        """,
        no_dedent=False,
    )


def test_no_implementations(project: Project) -> None:
    """
    This simple test creates a more complex module, with entities, implementations, index, etc.
    It then validates that the modules can be compiled and that its entities can be used.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module)

    entity = Entity(
        "Test",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type=InmantaListType(InmantaStringType),
                default="[]",
                description="This is a test list attribute",
            ),
        ],
        description="This is a test entity",
    )

    implement = Implement(
        path=[module.name],
        implementation=None,
        entity=entity,
        implementations=[],
    )

    module_builder.add_module_element(entity)
    module_builder.add_module_element(implement)

    # First generation should fail, we have an incomplete implement statement
    with pytest.raises(ValueError):
        module_builder.generate_module(Path(project._test_project_dir) / "libs")

    shutil.rmtree(str(Path(project._test_project_dir) / "libs" / module_builder._module.name))

    # Second generation should succeed, we set using_parents to true
    implement.using_parents = True
    module_builder.generate_module(Path(project._test_project_dir) / "libs")

    assert str(implement).strip() == "implement Test using parents"

    project.compile("import test")
