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

import inmanta
import pytest
from pytest_inmanta.plugin import Project

from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.inmanta.attribute import Attribute
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.implement import Implement
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.module import Module
from inmanta_module_factory.inmanta.typedef import TypeDef
from inmanta_module_factory.inmanta.types import InmantaListType, InmantaStringType


def test_simple(project: Project) -> None:
    """
    This simple test creates a simple module containing a type definition.  This type definition
    is used for an attribute of the single entity of this module.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module)

    typedef = TypeDef(
        "test",
        path=[module.name],
        base_type=InmantaStringType,
        constraint="std::length(self) > 10",
        description="String of minimum 10 characters",
    )

    entity = Entity(
        "Test",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type=typedef,
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

    module_builder.add_module_element(typedef)
    module_builder.add_module_element(entity)
    module_builder.add_module_element(implement)

    module_builder.generate_module(Path(project._test_project_dir) / "libs")

    project.compile(
        """
            import test

            test::Test(
                test="01234567890",
            )
        """,
        no_dedent=False,
    )

    # A string shorter than 10 character should fail
    with pytest.raises(inmanta.ast.AttributeException):
        project.compile(
            """
                import test

                test::Test(
                    test="0123456789",
                )
            """,
            no_dedent=False,
        )


def test_list(project: Project) -> None:
    """
    This simple test creates a simple module containing a type definition.  This type definition
    is used for a list attribute of the single entity of this module.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module)

    typedef = TypeDef(
        "test",
        path=[module.name],
        base_type=InmantaStringType,
        constraint="std::length(self) > 10",
        description="String of minimum 10 characters",
    )

    entity = Entity(
        "Test",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type=InmantaListType(typedef),
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

    module_builder.add_module_element(typedef)
    module_builder.add_module_element(entity)
    module_builder.add_module_element(implement)

    module_builder.generate_module(Path(project._test_project_dir) / "libs")

    project.compile(
        """
            import test

            test::Test(
                test=["01234567890"],
            )
        """,
        no_dedent=False,
    )

    # A string shorter than 10 character should fail
    with pytest.raises(inmanta.ast.AttributeException):
        project.compile(
            """
                import test

                test::Test(
                    test=["0123456789"],
                )
            """,
            no_dedent=False,
        )


def test_composed(project: Project) -> None:
    """
    This simple test creates a more complex module containing a few type definitions.
    One base typedef is defined in a different file, and two different typedefs are defined
    by adding constraints on this one.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module)

    typedef = TypeDef(
        "test",
        path=[module.name, "types"],
        base_type=InmantaStringType,
        constraint="std::length(self) >= 10",
        description="String of minimum 10 characters",
    )

    typedef1 = TypeDef(
        "test1",
        path=[module.name],
        base_type=typedef,
        constraint="std::length(self) <= 10",
        description="String of maximum 10 characters",
    )

    typedef2 = TypeDef(
        "test2",
        path=[module.name],
        base_type=typedef,
        constraint='std::validate_type("pydantic.constr", self, {"regex": "[a-z]+"})',
        description="String of alphabetical characters",
    )

    entity = Entity(
        "Test",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type=typedef1,
                description="This is a test attribute",
            ),
            Attribute(
                name="test2",
                inmanta_type=typedef2,
                default='"abcdefghij"',
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

    module_builder.add_module_element(typedef)
    module_builder.add_module_element(typedef1)
    module_builder.add_module_element(typedef2)
    module_builder.add_module_element(entity)
    module_builder.add_module_element(implement)

    module_builder.generate_module(Path(project._test_project_dir) / "libs")

    project.compile(
        """
            import test

            test::Test(
                test="0123456789",
            )
        """,
        no_dedent=False,
    )

    # A string shorter than 10 characters should fail
    with pytest.raises(inmanta.ast.AttributeException):
        project.compile(
            """
                import test

                test::Test(
                    test="012345678",
                )
            """,
            no_dedent=False,
        )

    # A string longer than 10 characters should fail
    with pytest.raises(inmanta.ast.AttributeException):
        project.compile(
            """
                import test

                test::Test(
                    test="01234567890",
                )
            """,
            no_dedent=False,
        )
