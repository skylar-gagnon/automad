import subprocess
import time
import sys

from modules.Measurement.Measurement import Measurement

class Measurement_LLM(Measurement):
    
    def __init__(self, conf_file):
        super().__init__(conf_file)

    def init(self):
        super().init()
        # self.time_to_measure = self.try_get_int_value("time_to_measure")
        self.time_to_measure = self.try_get_string_value("time_to_measure")

    def measure(self):

        #super().ping("10.42.0.50")
        
        super().copy_file_over_ftp()
        compilation_command = "cd "+ self.targetRunDir + ";gcc -O0 -Wall program.c -o individual &> tmp;" 
        execution_command = "cd "+ self.targetRunDir + ";"
        for cores in self.coresToUse:
            # execution_command += "taskset -c " + str(cores) + " ./individual >> tmp &;"
            execution_command += "timeout " + str(self.time_to_measure) + " taskset -c "  + str(cores) +  " ./individual >> tmp -k;"
        # execution_command += "cd " +self.targetRunDir + ";timeout " + str(self.time_to_measure) + "s; pkill individual &> /dev/null;" 
        output_command = "cd " + self.targetRunDir + "; cat tmp; rm individual;"# rm program.c; rm individual; rm tmp;";
        super().execute_ssh_command(compilation_command)
        super().execute_ssh_command(execution_command)
        stdout = super().execute_ssh_command(output_command)

        return stdout
        #
        ##count = 0.0
        ##current_measure = 0.0
        #current = []
        #for line in stdout:
        #    try:
        #        test = float(line)
        #        current.append(test)
        #        #current_measure = current_measure + test
        #        #count = count + 1.0
        #    except ValueError:
        #        print('Exception: line not current')
        #avg_current = sum(current) / len(current)
        ##current_measure /= count
        ##print(f'Avg I: {current_measure}')
        #
        #measurements = []
        #measurements.append(avg_current)
        #return measurements

