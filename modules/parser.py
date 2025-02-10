import sys, os
import modules.utils as utils

class Parser:
    def __init__(self):
        self.args = sys.argv[1:]

        # Setting default parameters
        self.runtime = 24
        self.unit = 'h'
        self.truetime = None
        self.model_name = "reddest-panda/AutoMAD-RL-2"
        self.config_name = "measure.xml"
        self.run_name = self.get_default_run_name()

        self.usage_msg = """

Usage: python3 run.py [OPTIONS] [RUNTIME]
Options:
-r        set run name
-m        set generation model name
-c        set config name for measurement class
runtime   set wall time for fuzzer to be run. Can be specified as
            seconds (s), minutes (m), or hours (h). Default unit
            is hours.

Example: python3 run.py 24h -m Model -c config.xml -r testrun"""

        # Parse command line arguments
        self.arg_parse()

    def get_default_run_name(self):
        os.makedirs("logs", exist_ok=True)
        num_runs = sum([subdirs.count("run_") for subdirs in os.listdir("logs")])
        self.run_name = f"run_{num_runs:4}"

    def check_flag(self, flag, param):
        try:
            index = self.args.index(flag)
            self.args.remove(flag)
            param = self.args.pop(index)
        except ValueError:
            param = param
        return param     

    def check_unit(self):
        match self.unit:
            case 's':
                self.truetime = self.runtime
            case 'm':
                self.truetime = self.runtime * 60
            case 'h':
                self.truetime = self.runtime * 60 * 60
            case _:
                utils.throw_error("invalid unit" + self.usage_msg)

    def check_runtime(self):
        try:
            if self.args[0][-1].isdigit():
                self.runtime = int(self.args.pop(0))
            else:
                self.runtime = int(self.args[0][0:-1])
                self.unit = self.args.pop(0)[-1]
        except IndexError:
            pass
        except ValueError:
            utils.throw_error("invalid runtime" + self.usage_msg)
            
    
    def get_truetime(self):
        self.check_runtime()
        self.check_unit()

    def arg_parse(self):
        # Checking for flags
        self.model_name = self.check_flag("-m", self.model_name)
        self.config_name = self.check_flag("-c", self.config_name)
        self.run_name = self.check_flag("-r", self.run_name)

        self.get_truetime()

        # Check remaining args
        if len(self.args) != 0:
            utils.throw_error("invalid arguments" + self.usage_msg)

    def print_launch_msg(self):
        print(f"Run Details\nRuntime: {self.runtime}{self.unit}\nModel Name: {self.model_name}\nConfig Name: {self.config_name}\nRun Name: {self.run_name}\n--------------------------------\nLaunching AutoMAD.")