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
import logging
from pathlib import Path

from pytest_inmanta.plugin import Project

from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.inmanta.attribute import Attribute
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.entity_relation import EntityRelation
from inmanta_module_factory.inmanta.implement import Implement
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.index import Index
from inmanta_module_factory.inmanta.module import Module

LOGGER = logging.getLogger(__name__)


def test_basic(project: Project) -> None:
    """
    This simple test creates a more complex module, with entities, implementations, index, etc.
    It then validates that the modules can be compiled and that its entities can be used.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module)

    base_entity = Entity(
        "Entity",
        path=["std"],
        fields=[],
    )

    entity = Entity(
        "Test",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type="string",
                description="This is a test attribute",
            ),
        ],
        description="This is a test entity",
        parents=[base_entity],
    )

    entity2 = Entity(
        "Test2",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type="string",
                description="This is a test attribute",
            ),
        ],
        description="This is another test entity",
        parents=[base_entity],
    )

    relation = EntityRelation(
        name="peer",
        path=[module.name],
        entity=entity,
        cardinality=(1, 1),
        peer=EntityRelation(
            name="peer",
            path=[module.name],
            entity=entity2,
            cardinality=(1, 1),
        ),
    )

    implementation = Implementation(
        name="none",
        path=["std"],
        entity=base_entity,
        content="",
    )

    implement = Implement(
        path=[module.name],
        implementation=implementation,
        entity=entity,
    )

    implement2 = Implement(
        path=[module.name],
        implementation=implementation,
        entity=entity2,
    )

    index = Index(
        path=[module.name],
        entity=entity,
        fields=[entity.attributes[0]],
        description="This is a test index",
    )

    index2 = Index(
        path=[module.name],
        entity=entity2,
        fields=[entity2.attributes[0], relation.peer],
        description="This is another test index",
    )

    module_builder.add_module_element(entity)
    module_builder.add_module_element(entity2)
    module_builder.add_module_element(relation)
    module_builder.add_module_element(implement)
    module_builder.add_module_element(implement2)
    module_builder.add_module_element(index)
    module_builder.add_module_element(index2)

    build_location = Path(project._test_project_dir) / "libs"
    module_builder.generate_module(build_location=build_location)

    LOGGER.debug((build_location / module.name / "model/_init.cf").read_text())

    project.compile(
        """
            import test

            t = test::Test(
                test="a",
                peer=t2,
            )
            t2 = test::Test2(
                test="b",
                peer=t,
            )
            a = test::Test[test="a"]
            b = test::Test2[test="b", peer=t]
        """,
        no_dedent=False,
    )
