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
from inmanta.parser.plyInmantaLex import keyworldlist

INDENT_PREFIX = "    "  # Four spaces

ASL_2_0_LICENSE = "ASL 2.0"
ASL_2_0_COPYRIGHT_HEADER_TMPL = '''
"""
    Copyright %(copyright)s

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: %(contact)s
    Author: %(author)s
"""
'''.strip(
    "\n"
)

EULA_LICENSE = "Inmanta EULA"
EULA_COPYRIGHT_HEADER_TMPL = '''
"""
    :copyright: %(copyright)s
    :contact: %(contact)s
    :author: %(author)s
    :license: Inmanta EULA
"""
'''.strip(
    "\n"
)

INMANTA_RESERVED_KEYWORDS = keyworldlist
