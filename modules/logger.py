import os, pprint

class Logger:
    def __init__(self, stats, path, run_name="run", top_n=3, verbose=False):
        self.path = path
        self.verbose = verbose
        self.stats = dict(stats) | {"TOTAL" : 0, "BEST_P2P" : [1 for _ in range(top_n)]}

        os.makedirs(f"{self.path}/logs", exist_ok=True)
        num_logs = len([s for s in os.listdir(f"{self.path}/logs") if run_name in s])
        self.run_name = f"{run_name}_{num_logs}"
        os.makedirs(f"{self.path}/logs/{self.run_name}/samples")

    def save_config(self, config):
        with open(f"{self.path}/logs/{self.run_name}/config", "w") as f:
                f.write(pprint.pformat(config))

    def update_flags(self, flags):
        for key in flags:
            self.stats[key] += flags[key]

    def update_p2p(self, p2p, response):
        if (p2p >= self.stats["BEST_P2P"][0]):
            self.stats["BEST_P2P"][0] = p2p
            self.stats["BEST_P2P"].sort()
            sample_num = len(os.listdir(f"{self.path}/logs/{self.run_name}/samples"))
            # Saves code from good samples
            with open(f"{self.path}/logs/{self.run_name}/samples/sample{sample_num}_{p2p}", "w") as f:
                f.write(response)

    def update(self, results, responses):
        for i, r in enumerate(results):
            self.update_flags(r["flags"])
            self.update_p2p(r["best_p2p"], responses[i])
            self.stats["TOTAL"] += 1
        if (self.verbose): print(self.stats)
        with open(f"{self.path}/logs/{self.run_name}/stats", "w") as f:
                f.write(self.stats.__str__())