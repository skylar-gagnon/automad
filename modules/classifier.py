import os, fileinput, re
from modules.Measurement.Measurement_LLM import Measurement_LLM

class Classifier:
    #* TESTED
    def __init__(self,
                 path,
                 train=False,
                 template_path="arm/pwr_template.c",
                 measure_config_path="configs/measure.xml",
                 max_ssh_attempts=3,
                 verbose=False
                ):
        
        self.path = path
        self.template_path = template_path
        self.max_ssh_attempts = max_ssh_attempts
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
            "PROC_FAIL" : 0,
            "MNTR_FAIL" : 0,
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
            code.append('"' + line + '\\n\\t"') # formats for c program
        return "\n".join(code)
    
    #! UNDER TEST
    def process_test(self, raw_snippet):
        lines = [l.strip() for l in raw_snippet.split("\n") if l.strip()] # removes excess whitespace and empty lines
        code = []
        if not self.train: lines = lines[2:]
        for line in lines: # Remove potentially unfinished line
            for subline in line.split("\\n"):
                # For some reason branches named with this scheme do not compile, and all branches are labeled as such in generated code, so switching them to reduce compile errors
                if (re.search("\.L\d+", subline) != None):
                    subline = subline.replace(".L", "BRANCH")
                elif subline.find(".cfi") != -1: # Remove cfi stuff
                    continue
                code.append('"' + subline + '\\n\\t"') # formats for c program
        return "\n".join(code[:-1])
    
    #* TESTED
    def compile(self, snippet):
        os.system(f"cp {self.path}/{self.template_path} {self.path}/tmp/cut.c")
        for line in fileinput.input(f"tmp/cut.c", inplace=1):
            if "<|SNIPPET|>" in line:
                print(f'{snippet}')
            else:
                print(line, end="")
        fileinput.close()
        return os.system(f"aarch64-linux-gnu-gcc -static -lpthread -O0 {self.path}/tmp/cut.c -o {self.path}/tmp/test 2> {self.path}/tmp/errors")

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
    
    #* TESTED
    def parse_pwr(self, raw_results):
        if (raw_results is None):
            best_p2p = -1
        elif (len(raw_results[1]) < 2):
            best_p2p = -1
            self.flags["MNTR_FAIL"] = 1
        else:
            currents = [int(reading) for reading in raw_results[1]]
            if (self.verbose) : print(len(currents)) #! DEBUG
            best_p2p = 0
            prev_curr = currents[0]
            for curr in currents[1:]:
                if abs(prev_curr - curr) > best_p2p:
                    best_p2p = abs(prev_curr - curr)
                prev_curr = curr
        return best_p2p
    
    #* TESTED
    def test_snippet(self, raw_snippet):
        self.clear_flags()
        snippet = self.process(raw_snippet)
        # If proccessing creates an empty snippet
        if (len(snippet) == 0):
            self.flags["PROC_FAIL"] = 1
            return None
        exit_status = self.compile(snippet)
        # If it fails to compile
        if (exit_status != 0):
            self.flags["COMP_FAIL"] = 1
            return None
        
        raw_results = self.execute()
        # If it fails to ssh
        if (raw_results is None):
            self.flags["SSH_FAIL"] = 1
            return None
        # If it fails to execute
        elif (len(raw_results[0]) != 0):
            self.flags["EXEC_FAIL"] = 1
            return None
        
        return raw_results

    #* TESTED
    def get_result(self, raw_snippet):
        raw_results = self.test_snippet(raw_snippet)
        self.cleanup()
        return {"best_p2p" : self.parse_pwr(raw_results), "flags" : self.flags}
    