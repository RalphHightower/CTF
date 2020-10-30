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
cfs_time_manager.py: CFS Time Manager for CTF.

- When initialized by the cFS plugin, the default CTF time manager (OS Time)
  is disabled, and the cFS time manager is used instead.

- The cFS time manager implements a serialized telemetry receive implementation
  as CTF instructions are "waiting".

- The cFS time manager also invokes the continuous verification checks
  between polls to ensure each packet is verified if a continuous verification
  exists.
"""


import traceback

from lib.Global import Config
from lib.exceptions import CtfTestError
from lib.time_interface import TimeInterface
import time
import logging as log

from plugins.cfs.pycfs.cfs_interface import CtfConditionError


class CfsTimeManager(TimeInterface):
    def __init__(self, cfs_targets):
        TimeInterface.__init__(self)
        self.ctf_verification_poll_period = Config.getfloat("core", "ctf_verification_poll_period", fallback=0.1)
        log.info("CfsTimeManager Initialized. Verification Poll Period = {}."
                 .format(self.ctf_verification_poll_period))
        self.cfs_targets = cfs_targets

    def handle_test_exception_during_wait(self, e, msg, do_raise=False):
        log.error("Error: {}".format(msg))
        log.debug(e)
        if do_raise:
            raise e

    def wait(self, seconds):
        super().wait(seconds)
        start_time = self.exec_time
        while self.exec_time < start_time + seconds:
            try:
                self.pre_command()
            except CtfTestError as e:
                self.handle_test_exception_during_wait(e, "CfsTimeManager: Pre-Command Failed", True)

            try:
                self.post_command()
            except CtfTestError as e:
                self.handle_test_exception_during_wait(e, "CfsTimeManager: Post-Command Failed", True)

            time.sleep(self.ctf_verification_poll_period)
            self.exec_time += self.ctf_verification_poll_period

    def pre_command(self):
        super().pre_command()
        for target in self.cfs_targets.values():
            try:
                target.cfs.read_sb_packets()
            except Exception as e:
                log.error("Failed to receive CFS Telemetry Packets for CFS Target: {}."
                          .format(target.config.name))
                log.debug(traceback.format_exc())
        try:
            self.run_continuous_verifications()
        except CtfConditionError as e:
            # Raise ConditionError to Test in order to fail the test...
            raise e
        except CtfTestError as e:
            # Raise other generic CtfTestError to Test to react to it if needed...
            log.debug(e)
            raise e

    def run_continuous_verifications(self):
        try:
            for target in self.cfs_targets.values():
                if target is not None and target.cfs is not None:
                    target.cfs.check_tlm_conditions()
        except CtfConditionError as e:
            log.error("Test condition(s) failed in Post Command.")
            raise e

    def post_command(self):
        super().post_command()
