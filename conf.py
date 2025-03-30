#    Copyright 2025 AzureTecDevs
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import uuid

# The type of server. Valid options are: 'chat', 'filesys'
SERVER_TYPE = 'chat'
S_TYPE = SERVER_TYPE
SERVER_UUID = str(uuid.uuid4()) # changing this is not recomended
SERVER_VERSION = ['1.0.0', 'openServer'] # [VERSION, SERVER_BRAND]

# IMPORTANT: The server's IP address
IP = '127.0.0.1'

# The server's Message of the day (MOTD) that is sent to clients when they connect.
MESSAGE = 'Welcome!'

# The server's display name
SERVER_DISPLAY_NAME = 'Demo Server 1'

# Advanced configuration
MOTD = {'type': 'welcome', 'message': MESSAGE, 'server_uuid': SERVER_UUID, 
        'server_version': SERVER_VERSION[0], 'server_brand': SERVER_VERSION[1],
        'server_type': SERVER_TYPE, 'server_appn': SERVER_DISPLAY_NAME}

# Extra information that will be injected into each BROADCAST.
EXTRA_PARAMS = {}
