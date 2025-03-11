import os
import modules.utils as utils

class Logger:

    #TODO
    def __init__(self, name, stats):
        self.name = name
        self.stats = dict(stats) | {"TOTAL" : 0, "BEST_P2P" : 1}
        
        try:
            os.makedirs(f"logs/{self.name}/samples")
        except FileExistsError:
            utils.throw_error(f"run named {name} already exists\n")

    def update_flags(self, flags):
        for key in flags:
            self.stats[key] += flags[key]

    def update_p2p(self, p2p, response):
        if (p2p >= self.stats["BEST_P2P"]):
            self.stats["BEST_P2P"] = p2p
            sample_num = len(os.listdir(f"logs/{self.name}/samples"))
            # Saves code from good samples
            with open(f"logs/{self.name}/samples/sample{sample_num}_{p2p}", "w") as f:
                f.write(response)

    def update(self, results, responses):
        for i, r in enumerate(results):
            self.update_flags(r["flags"])
            self.update_p2p(r["best_p2p"], responses[i])
            self.stats["TOTAL"] += 1
        with open(f"logs/{self.name}/stats", "w") as f:
                f.write(self.stats.__str__())