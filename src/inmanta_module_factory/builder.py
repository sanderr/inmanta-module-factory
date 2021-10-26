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
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional, Set

import yaml

from inmanta_module_factory.inmanta.module import Module
from inmanta_module_factory.inmanta.module_element import (
    DummyModuleElement,
    ModuleElement,
)
from inmanta_module_factory.inmanta.plugin import Plugin

LOGGER = logging.getLogger(__name__)


class InmantaModuleBuilder:
    def __init__(self, module: Module) -> None:
        self._module = module
        self._model_files: Dict[str, List[ModuleElement]] = dict()
        self._plugins: List[Plugin] = list()

        # Ensuring the model folder exists
        self.add_module_element(DummyModuleElement([module.name]))

    def add_module_element(self, module_element: ModuleElement) -> None:
        if not module_element.path[0] == self._module.name:
            raise RuntimeError(
                "The module elements should have a path starting with the module name.  "
                f"Got '{module_element.path[0]}', expected '{self._module.name}'"
            )

        if module_element.path_string in self._model_files.keys():
            self._model_files[module_element.path_string].append(module_element)
        else:
            self._model_files.setdefault(module_element.path_string, [module_element])

    def add_plugin(self, plugin: Plugin) -> None:
        self._plugins.append(plugin)

    def generate_model_file(
        self,
        build_location: Path,
        file_key: str,
        force: bool = False,
        copyright_header_template: Optional[str] = None,
    ) -> Optional[Path]:
        if file_key not in self._model_files.keys():
            raise RuntimeError(
                "Tried to generate a file that is not part of the model, "
                f"{file_key} is not in {list(self._model_files.keys())}"
            )

        module_elements = self._model_files[file_key]
        module_elements.sort(key=lambda element: element.ordering_key)
        if not module_elements:
            LOGGER.warning(f"No module elements found for {file_key}, skipping.")
            return None

        file_path = build_location / Path(
            self._module.name,
            "model",
            "/".join(module_elements[0].path[1:]),
            "_init.cf",
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            LOGGER.warning(f"Generating a file where a file already exists: {str(file_path)}")
            if not force:
                raise RuntimeError(f"Generating this file would have overwritten and existing one: {str(file_path)}")

        imports: Set[str] = set()
        for module_element in module_elements:
            imports = imports.union(module_element.get_imports())

        import_list = [f"import {import_value}" for import_value in imports]
        import_list.sort()

        file_content = (
            self._module.file_header(copyright_header_template)
            + "\n"
            + "\n".join(import_list)
            + "\n\n"
            + "\n".join([str(module_element) for module_element in module_elements])
        )

        file_path.write_text(file_content)

        return file_path

    def generate_plugin_file(
        self, build_location: Path, force: bool = False, copyright_header_template: Optional[str] = None
    ) -> Path:
        self._plugins.sort(key=lambda plugin: plugin.name)

        file_path = build_location / Path(self._module.name, "plugins/__init__.py")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            LOGGER.warning(f"Generating a file where a file already exists: {str(file_path)}")
            if not force:
                raise RuntimeError(f"Generating this file would have overwritten and existing one: {str(file_path)}")

        imports: Set[str] = set()
        for plugin in self._plugins:
            imports = imports.union(plugin.get_imports())

        import_list = list(imports)
        import_list.sort()

        file_content = (
            self._module.file_header(copyright_header_template)
            + "\n"
            + "\n".join(import_list)
            + "\n\n\n"
            + "\n\n".join([str(plugin) for plugin in self._plugins])
        )

        file_path.write_text(file_content)

        return file_path

    def generate_model_test(
        self, build_location: Path, force: bool = False, copyright_header_template: Optional[str] = None
    ) -> Path:
        file_path = build_location / Path(self._module.name, "tests/test_basics.py")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            LOGGER.warning(f"Generating a file where a file already exists: {str(file_path)}")
            if not force:
                raise RuntimeError(f"Generating this file would have overwritten and existing one: {str(file_path)}")

        file_content = (
            self._module.file_header(copyright_header_template)
            + "\n"
            + "from pytest_inmanta.plugin import Project\n\n\n"
            + dedent(
                f"""
                def test_basics(project: Project) -> None:
                    project.compile("import {self._module.name}")
                """.strip(
                    "\n"
                )
            )
        )

        file_path.write_text(file_content)

        return file_path

    def generate_module(
        self, build_location: Path, force: bool = False, copyright_header_template: Optional[str] = None
    ) -> None:
        module_path = build_location / Path(self._module.name)
        if module_path.exists():
            if not force:
                raise RuntimeError(f"Generating this module would have overwritten the following path: {str(module_path)}")

            shutil.rmtree(str(module_path))

        module_path.mkdir(parents=True)

        self.generate_plugin_file(build_location, force, copyright_header_template)

        for file_key in list(self._model_files.keys()):
            if file_key == self._module.name:
                continue

            splitted_key = file_key.split("::")
            parent_path = splitted_key[0]
            for part in splitted_key[1:]:
                parent_path += f"::{part}"
                if parent_path not in self._model_files:
                    self._model_files[parent_path] = [DummyModuleElement(parent_path.split("::"))]

        for file_key in self._model_files.keys():
            self.generate_model_file(build_location, file_key, force, copyright_header_template)

        self.generate_model_test(build_location, force, copyright_header_template)

        file_path = module_path / Path("module.yml")
        file_path.touch()
        with open(str(file_path), "w") as f:
            yaml.dump(self._module.as_dict(), f)
            f.close()
