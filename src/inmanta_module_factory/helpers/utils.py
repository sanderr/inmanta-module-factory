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
import logging
import pathlib
import re
import subprocess
import sys
import tempfile

import inmanta
import inmanta.module

from inmanta_module_factory.helpers import const

LOGGER = logging.getLogger(__name__)


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
    if output in const.INMANTA_RESERVED_KEYWORDS:
        output = f"x_{output}"

    return output


def copyright_header_from_module(existing_module: inmanta.module.Module) -> str:
    """
    This helper function can help build a template header from an already existing module.
    So that it is used by the generator when the module is extended for example.
    """
    copyright_header_tmpl = None
    copyright_header_source_file = pathlib.Path(existing_module.path, existing_module.MODEL_DIR, "_init.cf")
    if not copyright_header_source_file.exists() or not copyright_header_source_file.is_file():
        raise ValueError(f"The path {copyright_header_source_file} doesn't point to a file.")

    model_root_content = copyright_header_source_file.read_text()
    docstring_blocks = model_root_content.split('"""')
    if not docstring_blocks:
        raise ValueError(f"Failed to extract copyright header from file {copyright_header_source_file}")

    copyright_header_tmpl = '"""' + docstring_blocks[1] + '"""'
    return copyright_header_tmpl


def fix_module_linting(existing_module: inmanta.module.Module) -> None:
    """
    Fix the linting of an existing (generated or not) module.
    """
    # Setup a virtual env, install dev dependencies and fix module linting
    with tempfile.TemporaryDirectory() as tmpdir:
        fix_linting_command = [
            "bash",
            "-c",
            (
                f"{sys.executable} -m venv {tmpdir}; "
                f"source {tmpdir}/bin/activate; "
                "pip install -U pip; "
                "pip install -r requirements.dev.txt; "
                f"black tests {existing_module.get_plugin_dir()}; "
                f"isort tests {existing_module.get_plugin_dir()}; "
                f"flake8 tests {existing_module.get_plugin_dir()}"
            ),
        ]
        LOGGER.debug(f"Running command {fix_linting_command}")
        result = subprocess.Popen(
            args=fix_linting_command,
            cwd=existing_module.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = result.communicate()
        LOGGER.debug(stdout)
        LOGGER.debug(stderr)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fix the linting of the module (return code = {result.returncode}):\n{stderr}")


def remove_watermarked_files(directory: pathlib.Path) -> None:
    """
    Recursively traverse the directory and remove all files containing the "generated file"
    watermark.  If an empty folder is found, it is removed as well.
    """
    for file in directory.glob("*"):
        if file.is_dir():
            remove_watermarked_files(file)

            try:
                # Tries to get the first file that is still in the folder
                # If no file can be found, a StopIteration will be raised
                # and we know we can delete the full folder.
                next(file.glob("*"))
            except StopIteration:
                file.rmdir()

            continue

        if not (file.name.endswith(".py") or file.name.endswith(".cf")):
            # The file is not safe to read and we wouldn't have added
            # a water mark in there
            continue

        if const.GENERATED_FILE_MARKER in file.read_text(encoding="utf-8"):
            file.unlink()
