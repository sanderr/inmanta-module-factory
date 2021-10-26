# Inmanta module factory

This library is an inmanta module factory, it can help you automate the generation of inmanta v1 modules.

This package contains a few python classes that represents components of an inmanta module:
 - `Entity`: Represents an `entity` definition.
 - `Implement`: Represents an `implement` statement.
 - `Implementation`: Represents an `implementation` definition.
 - `EntityRelation`: Represents an relation between two entities.
 - `Index`: Represents an `index` statement.
 - `Attribute`: Represents an entity attribute.
 - `Module`: Represents the module itself.
 - `Plugin`: Represents a plugin.

All those classes can be instantiated and passed to an `InmantaModuleBuilder` instance to generate a module.  The module generator will build all required model files, the plugin file, and a simple test.

## Example

```python
from pathlib import Path

from inmanta_module_factory.inmanta.attribute import Attribute, InmantaPrimitiveList
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.entity_relation import EntityRelation
from inmanta_module_factory.inmanta.implement import Implement
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.index import Index
from inmanta_module_factory.inmanta.module import Module
from inmanta_module_factory.builder import InmantaModuleBuilder


module = Module(name="test")
module_builder = InmantaModuleBuilder(module)

entity = Entity(
    name="Test",
    path=[module.name],
    attributes=[
        Attribute(
            name="test",
            inmanta_type=InmantaPrimitiveList("string"),
            default="[]",
            description="This is a test attribute",
        )
    ],
    description="This is a test entity",
)

implementation = Implementation(
    name="test",
    path=[module.name],
    entity=entity,
    content="",
    description="This is a test implementation",
)

implement = Implement(
    path=[module.name],
    implementation=implementation,
    entity=entity,
)

index = Index(
    path=[module.name],
    entity=entity,
    attributes=entity.attributes,
    description="This is a test index",
)

relation = EntityRelation(
    name="tests",
    path=[module.name],
    entity=entity,
    arity=(0, None),
    peer=EntityRelation(
        name="",
        path=[module.name],
        entity=entity,
        arity=(0, 0),
    ),
)

module_builder.add_module_element(entity)
module_builder.add_module_element(implementation)
module_builder.add_module_element(implement)
module_builder.add_module_element(index)
module_builder.add_module_element(relation)

module_builder.generate_module(
    build_location=Path("/home/guillaume/Documents/terraform-dev/libs/"),
    force=True,
)
```

**Tips**  The path attribute that most of the previously mentioned classes take in their constructor can be used to specify where in the module the element should be located.  The path is a list of strings.  
If an entity has as path: `["test", "a", "b"]` and as name: `C`, the entity will will be placed in the module `test` in the file `model/a/b/_init.cf` (starting from the root of the module).  To import it, you will then use the following statement: `import test::a::b`, and to use it: `test::a::b::C(...)`.

In the example above, the entity named `Test` is at the root of its module, so the path only contains the module name (`test`).  It can be used in any project by using its full path, `test::Test`.

## Recommended usage
Even though this package can be used standalone to generate modules, it is very verbose and it probably takes more time to generate a module by describing all its components in python with this library than directly writing it in Inmanta language.  This module is meant to be used with any other tool to generate modules automatically (from some schema input, that logic has to be handled by the parser using this package).

An example of such usage is the terraform module generator, which parse the schema of a terraform provider and converts it to the previously presented objects.  The module builder can then be used to generate the inmanta module.
