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
from pathlib import Path

from pytest_inmanta.plugin import Project

from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.inmanta.attribute import Attribute
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.implement import Implement
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.module import Module


def test_foreign_implementation(project: Project) -> None:
    """
    This simple test creates a module with an entity using the implementation of another module.
    It then tries to compile it and use of of these entities.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module)

    entity = Entity(
        "Test",
        path=[module.name],
        attributes=[
            Attribute(
                name="test",
                inmanta_type="string",
                description="This is a test attribute",
            ),
        ],
        description="This is a test entity",
    )

    implement = Implement(
        path=[module.name],
        implementation=Implementation(
            name="none",
            path=["std"],
            entity=entity,
            content="",
        ),
        entity=entity,
    )

    module_builder.add_module_element(entity)
    module_builder.add_module_element(implement)

    module_builder.generate_module(Path(project._test_project_dir) / "libs")

    project.compile(
        """
            import test

            test::Test(
                test="a",
            )
        """,
        no_dedent=False,
    )
