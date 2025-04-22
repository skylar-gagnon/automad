import os, fileinput, re
import numpy as np
from modules.Measurement.Measurement_LLM import Measurement_LLM
from time import sleep

class Classifier:
    #* TESTED
    def __init__(self,
                 path,
                 train=False,
                 template_path="dut/pwr_template.c",
                 measure_config_path="configs/measure.xml",
                 max_ssh_attempts=5,
                 max_patch_attempts=1,
                 verbose=False
                ):
        
        self.path = path
        self.template_path = template_path
        self.max_ssh_attempts = max_ssh_attempts
        self.max_patch_attempts = max_patch_attempts
        self.train = train
        self.verbose = verbose

        self.measurement = Measurement_LLM(f"{self.path}/{measure_config_path}")
        self.measurement.init()
        self.measurement.set_source_file_path(f"{self.path}/tmp/test")

        # Add more flags as needed
        self.flags = {
            "SSH_FAIL"  : 0,
            "COMP_FAIL" : 0,
            "EXEC_FAIL" : 0,
            "PROC_FAIL" : 0
        }

        os.makedirs(f"{self.path}/tmp", exist_ok=True)

    #* TESTED
    def clear_flags(self):
        self.flags = dict.fromkeys(self.flags, 0)

    #*TESTED
    def cleanup(self):
        if (len(os.listdir(f"{self.path}/tmp")) > 0):
            os.system(f"rm -r {self.path}/tmp/*")

    #* TESTED
    def process(self, raw_snippet):
        lines = [l.strip() for l in raw_snippet.split("\n") if l.strip()] # removes excess whitespace and empty lines
        code = []
        if not self.train: lines = lines[2:]
        for line in lines[:-1]: # Remove potentially unfinished line
            # For some reason branches named with this scheme do not compile, and all branches are labeled as such in generated code, so switching them to reduce compile errors
            if (re.search("\.L\d+", line) != None):
                line = line.replace(".L", "BRANCH")
            elif line.find(".cfi") != -1: # Remove cfi stuff
                continue
            elif line.find("fork") != -1:
                continue
            code.append('"' + line + '\\n\\t"') # formats for c program
        return "\n".join(code)

    #* TESTED
    def patch_snippet(self, snippet):
        # Ignores first compile
        if (os.path.exists(f"{self.path}/tmp/errors")):
            # Get error msg
            with open(f"{self.path}/tmp/errors", 'r', errors='ignore') as f:
                err_msg = f.read()
            
            # Patch
            for line in err_msg.split("\n"):
                undefined_ref = re.search("(?<=undefined reference to `)(\S+)(?=')", line)
                if undefined_ref != None:
                    undefined_ref = undefined_ref.group(0) # Converts to string
                    if undefined_ref.count("BRANCH") > 0: # Adds in unresolved branches
                        snippet = f'{snippet}\n"{undefined_ref}:\\n\\t"'
                        snippet += f'\n"nop\\n\\t"'
                    else: # Changes out undefined function calls
                        snippet = snippet.replace(undefined_ref, "dummy_func_call")
        return snippet

    #* TESTED
    def attempt_compile(self, snippet):
        os.system(f"cp {self.path}/{self.template_path} {self.path}/tmp/cut.c")
        for line in fileinput.input(f"tmp/cut.c", inplace=1):
            if "<|SNIPPET|>" in line:
                print(f'{snippet}')
            else:
                print(line, end="")
        fileinput.close()
        return os.system(f"aarch64-linux-gnu-gcc -static -lpthread -O0 {self.path}/tmp/cut.c -o {self.path}/tmp/test 2> {self.path}/tmp/errors")

    #* TESTED
    def compile(self, snippet):
        for _ in range(self.max_patch_attempts + 1):
            snippet = self.patch_snippet(snippet)
            exit_status = self.attempt_compile(snippet)
            if (exit_status == 0):
                break
        return exit_status, snippet

    #* TESTED
    def execute(self):
        for _ in range(self.max_ssh_attempts):
            try:
                raw_results = self.measurement.measure()
                return raw_results
            except Exception:
                pass
        return None

    #* TESTED
    def parse_pmc(self, raw_results):
        results = {}
        for line in raw_results:
            name, value = line.split(':')
            results.update({name : int(value)})
        return results
    
    def remove_outliers(self, data, threshold=1.5):
        if len(data) == 0:
            return data
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        return [x for x in data if lower_bound <= x <= upper_bound]

    #* TESTED
    def parse_pwr(self, raw_results):
        if (raw_results is None):
            max_p2p = -1
            avg_p2p = -1
        else:
            currents = [int(reading) for reading in raw_results[1] if reading.strip()]
            if (self.verbose) : print(len(currents)) #! DEBUG
            max_p2p = 0
            avg_p2p = 0.0
            prev_curr = currents[0]
            for curr in currents[1:]:
                p2p = abs(prev_curr - curr)
                if p2p > max_p2p: max_p2p = p2p
                avg_p2p += p2p
                prev_curr = curr
            avg_p2p = avg_p2p / float(len(currents) - 1)
        return max_p2p, avg_p2p
    
    #* TESTED
    def test_snippet(self, raw_snippet):
        self.clear_flags()
        snippet = self.process(raw_snippet)
        # If proccessing creates an empty snippet
        if (len(snippet) == 0):
            self.flags["PROC_FAIL"] = 1
            return None, snippet
        
        exit_status, snippet = self.compile(snippet)
        # If it fails to compile
        if (exit_status != 0):
            self.flags["COMP_FAIL"] = 1
            return None, snippet
        
        raw_results = self.execute()
        # If it fails to ssh
        if (raw_results is None):
            self.flags["SSH_FAIL"] = 1
            return None, snippet
        # If it fails to execute
        elif (len(raw_results[1]) < 2):
            if (self.verbose): print(f"STDER: {raw_results[0]}") #! DEBUG
            self.flags["EXEC_FAIL"] = 1
            return None, snippet
        
        return raw_results, snippet

    #* TESTED
    def get_result(self, raw_snippet):
        raw_results, snippet = self.test_snippet(raw_snippet)
        self.cleanup()
        max_p2p, avg_p2p = self.parse_pwr(raw_results)
        return {"max_p2p" : max_p2p, "avg_p2p" : avg_p2p, "snippet" : snippet, "flags" : self.flags}
    
    #? ------------- DEMO CODE ------------- ?#

    def demo_test_snippet(self, raw_snippet):
        self.clear_flags()
        snippet = self.process(raw_snippet)
        with open("demo", "w") as f:
            f.write(f"Processed Snippet:\n{snippet}")
        sleep(5)
        # If proccessing creates an empty snippet
        if (len(snippet) == 0):
            self.flags["PROC_FAIL"] = 1
            return None, snippet
        
        exit_status, snippet = self.compile(snippet)
        with open("demo", "w") as f:
            f.write(f"Patched Snippet:\n{snippet}")
        sleep(5)
        os.system(f"cp {self.path}/tmp/cut.c demo")
        sleep(10)
        # If it fails to compile
        if (exit_status != 0):
            self.flags["COMP_FAIL"] = 1
            return None, snippet
        
        raw_results = self.execute()
        # If it fails to ssh
        if (raw_results is None):
            self.flags["SSH_FAIL"] = 1
            return None, snippet
        # If it fails to execute
        elif (len(raw_results[1]) < 2):
            if (self.verbose): print(f"{raw_results[0]}") #! DEBUG
            self.flags["EXEC_FAIL"] = 1
            return None, snippet
        
        with open("demo", "w") as f:
            f.write(f"First 100 Measurements:\n{str(raw_results[1][:100])}")
        sleep(5)
        return raw_results, snippet

    def demo_parse_pwr(self, raw_results):
        if (raw_results is None):
            max_p2p = -1
            avg_p2p = -1
            currents = []
        else:
            currents = [int(reading) for reading in raw_results[1] if reading.strip()]
            if (self.verbose) : print(len(currents)) #! DEBUG
            max_p2p = 0
            avg_p2p = 0.0
            prev_curr = currents[0]
            for curr in currents[1:]:
                p2p = abs(prev_curr - curr)
                if p2p > max_p2p: max_p2p = p2p
                avg_p2p += p2p
                prev_curr = curr
            avg_p2p = avg_p2p / float(len(currents) - 1)
            with open("demo", "w") as f:
                f.write(f"Stats:\n\tAvg: {avg_p2p} mA\n\tMax: {max_p2p} mA")
            sleep(5)
        return max_p2p, avg_p2p, currents
    
    def demo(self, raw_snippet):
        with open("demo", "w") as f:
            f.write(f"Snippet from Model:\n{raw_snippet}")
        sleep(5)
        raw_results, snippet = self.demo_test_snippet(raw_snippet)
        self.cleanup()
        max_p2p, avg_p2p, currs = self.demo_parse_pwr(raw_results)
        return {"max_p2p" : max_p2p, "avg_p2p" : avg_p2p, "snippet" : snippet, "flags" : self.flags}, currs