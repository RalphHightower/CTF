# MSC-26646-1, "Core Flight System Test Framework (CTF)"
#
# Copyright (c) 2019-2020 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is governed by the NASA Open Source Agreement (NOSA) License and may be used,
# distributed and modified only pursuant to the terms of that agreement.
# See the License for the specific language governing permissions and limitations under the
# License at https://software.nasa.gov/ .
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either expressed or implied.

"""
ccsds_secondary_header.py: Implementation of the secondary header structure that is shared by CCSDS V1 and V2 for CFE
"""


import ctypes


class CcsdsSecondaryCmdHeader(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("function_code", ctypes.c_uint8),
        ("checksum", ctypes.c_uint8)
    ]

    def set_function_code(self, function_code: int) -> None:
        self.function_code = function_code

    def set_checksum(self, checksum: int) -> None:
        self.checksum = checksum

    def get_function_code(self) -> int:
        return self.function_code

    def get_checksum(self) -> int:
        return self.checksum


class CcsdsSecondaryTlmHeader(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("timestamp_seconds", ctypes.c_uint32),
        ("timestamp_subseconds", ctypes.c_uint16),
    ]
