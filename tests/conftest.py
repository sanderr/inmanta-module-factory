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
import os
import shutil
import sys
import tempfile
from typing import Callable, Generator, Tuple

import pytest
import yaml
from _pytest.monkeypatch import MonkeyPatch
from inmanta import module
from pytest_inmanta.plugin import Project, get_module_data

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def project_shared(project_factory: Callable[[bool], "Project"]) -> Generator["Project", None, None]:
    """
    Overwriting the fixture from pytest_inmanta with a function scope
    """
    yield project_factory(True)


# Temporary workaround for plugins loading multiple times (inmanta/pytest-inmanta#49)
@pytest.fixture(scope="function")
def project_shared_no_plugins(project_factory: Callable[[bool], "Project"]) -> Generator["Project", None, None]:
    """
    Overwriting the fixture from pytest_inmanta with a function scope
    """
    yield project_factory(False)


@pytest.fixture(scope="function")
def project_factory(monkeypatch: MonkeyPatch) -> Generator[Callable[[bool], "Project"], None, None]:
    """
    Overwriting the fixture from pytest_inmanta with a function scope and a modified behavior:
        - The fixture doesn't try to get the module in this context as we are now in a module context
        - The fixture overwrites the method pytest_inmanta.plugin.get_module to make it return
          the std module. This means that only std module will be initially loaded in the project.
    """
    import pytest_inmanta.plugin

    _sys_path = sys.path
    test_project_dir = tempfile.mkdtemp()
    libs_dir = os.path.join(test_project_dir, "libs")
    os.mkdir(libs_dir)
    env_dir = os.path.join(test_project_dir, ".env")

    project_file = {
        "name": "testcase",
        "repo": ["https://github.com/inmanta/"],
        "downloadpath": "libs",
        "modulepath": ["libs"],
        "install_mode": "master",
    }
    with open(os.path.join(test_project_dir, "project.yml"), "w+") as f:
        yaml.dump(project_file, f)

    with open(os.path.join(test_project_dir, "main.cf"), "w+") as f:
        f.write("import std")

    # Ensure the std module is installed
    project = module.Project(path=test_project_dir, autostd=True, venv_path=env_dir)
    project.set(project)
    project.install_modules()

    def get_module() -> Tuple[module.ModuleV1, str]:
        std_module_dir = os.path.join(libs_dir, "std")
        return module.ModuleV1(project, std_module_dir), std_module_dir

    monkeypatch.setattr(pytest_inmanta.plugin, "get_module", get_module)

    def create_project(load_plugins: bool = True) -> Project:
        test_project = Project(test_project_dir, env_path=env_dir, load_plugins=load_plugins)
        test_project.create_module(
            "unittest",
            initcf=get_module_data("init.cf"),
            initpy=get_module_data("init.py"),
        )
        return test_project

    yield create_project

    try:
        shutil.rmtree(test_project_dir)
    except PermissionError:
        LOGGER.warning(
            "Cannot cleanup test project %s. This can be caused because we try to remove a virtual environment, "
            "loaded by this python process. Try to use a shared environment with --venv",
            test_project_dir,
        )

    sys.path = _sys_path
