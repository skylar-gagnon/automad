import subprocess
import time
import sys

from modules.Measurement.Measurement import Measurement

class Measurement_LLM(Measurement):
    
    def __init__(self, conf_file):
        super().__init__(conf_file)

    def init(self):
        super().init()
        self.time_to_measure = self.try_get_string_value("time_to_measure")

    def measure(self):
        super().copy_file_over_ftp()

        cd_command = "cd "+ self.targetRunDir + ";"
        execution_command = "chmod +x test;timeout " + str(self.time_to_measure) + " ./test 2> tmp -k;"
        error_command = "cat tmp"
        log_command = "cat curr2_log; rm curr2_log; touch curr2_log"

        super().execute_ssh_command(cd_command + execution_command)
        stderr = super().execute_ssh_command(cd_command + error_command)
        log = super().execute_ssh_command(cd_command + log_command)
        return [stderr, log]