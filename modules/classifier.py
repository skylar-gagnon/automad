import os, fileinput, re
from modules.Measurement.Measurement_LLM import Measurement_LLM
import modules.utils as utils

class Classifier:

    #* TESTED
    def __init__(self, template_name, config_name, max_ssh_attempts=3):
        try:
            self.measurement = Measurement_LLM(config_name)
            self.measurement.init()
        except FileNotFoundError:
            utils.throw_error(f"no file named {config_name} found")

        try:
            test = open(template_name, 'r')
            self.template_name = template_name
        except FileNotFoundError:
            utils.throw_error(f"no file named {template_name} found")

        self.max_ssh_attempts = max_ssh_attempts

        # Add more flags as needed
        self.flags = {
            "PROCESS_FAILURE" : 0,
            "SSH_FAILURE" : 0,
        }

        os.makedirs("tmp", exist_ok=True)

    #* TESTED
    def clear_flags(self):
        self.flags = dict.fromkeys(self.flags, 0)

    #*TESTED
    def cleanup(self):
        os.system("rm test.log; rm tmp/*")

    #TODO: Processes a snippet into serial and parallel form, sets process fail flag
    def process(self, raw_snippet):
        return raw_snippet
    
    #* TESTED
    def prep_program(self, snippet):
        os.system(f"cp {self.template_name} tmp/test_snippet.c")
        for line in fileinput.input(f"tmp/test_snippet.c", inplace=1):
            if "<|snippet|>" in line:
                print(f'{snippet}')
            else:
                print(line, end="")
        fileinput.close()
        self.measurement.set_source_file_path(f"tmp/test_snippet.c")

    #* TESTED
    def run(self, snippet):
        self.prep_program(snippet)
        for _ in range(self.max_ssh_attempts):
            try:
                raw_results = self.measurement.measure()
                return raw_results
            except Exception:
                pass
        
        self.flags["SSH_FAILURE"] = 1
        return

    #TODO: Parses the results after running the code 
    def parse(self, raw_results):
        results = {}
        for line in raw_results:
            name, value = line.split(':')
            results.update({name : int(value)})
        return results
    
    #? Unit tests
    def get_results(self, snippet):
        raw_results = self.run(snippet)
        return self.parse(raw_results)
    
    #TODO: Analyzes the parsed results, sets flags 
    def analyze(self, parallel_result, serial_result):
        return

    #? Unit tests
    def check(self, raw_snippets):
        results = []

        for raw_snippet in raw_snippets:
            parallel, serial = self.process(raw_snippet)
            result = (self.get_results(parallel, "parallel.c"), self.get_results(serial, "serial.c"))
            results.append(self.analyze(result))

        self.cleanup()
        return results