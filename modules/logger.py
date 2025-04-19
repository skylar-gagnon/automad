import os, pprint
import pandas as pd
from datetime import datetime

class Logger:
    def __init__(self,
                 start_time,
                 stats,
                 path,
                 run_name="run",
                 top_n=5,
                 save_snippets=False,
                 verbose=False
                 ):
        
        self.start_time = start_time
        self.stats = dict(stats) | {"TOTAL" : 0, "BEST_AVG_P2P" : [0 for _ in range(top_n)]}
        self.path = path
        self.save_snippets = save_snippets
        self.verbose = verbose

        os.makedirs(f"{self.path}/logs", exist_ok=True)
        num_logs = len([s for s in os.listdir(f"{self.path}/logs") if run_name in s])
        self.run_name = f"{run_name}_{num_logs}"
        os.makedirs(f"{self.path}/logs/{self.run_name}/samples")

    def save_config(self, config):
        with open(f"{self.path}/logs/{self.run_name}/config", "w") as f:
            f.write(pprint.pformat(config))

    def update_csv(self, responses, results):
        df = pd.DataFrame({
            "response" : responses,
            "snippet"  : [r.get("snippet") for r in results],
            "max_p2p"  : [r.get("max_p2p") for r in results],
            "avg_p2p"  : [r.get("avg_p2p") for r in results]
        })
        
        if (os.path.exists(f"{self.path}/logs/{self.run_name}/saved_data.csv")):
            record = pd.read_csv(f"{self.path}/logs/{self.run_name}/saved_data.csv")
            df = pd.concat([record[["response", "snippet", "max_p2p", "avg_p2p"]], df], axis = 0, ignore_index=True)
        df.to_csv(f"{self.path}/logs/{self.run_name}/saved_data.csv")

    def print_verbose(self):
        time = datetime.now().strftime('\033[1m\033[94m%Y-%m-%d \033[92m%H:%M:%S\033[0m')
        print(f"{time} {self.stats}")

    def update_flags(self, flags):
        for key in flags:
            self.stats[key] += flags[key]

    def update_p2p(self, p2p, response):
        if (p2p >= self.stats["BEST_AVG_P2P"][0]):
            self.stats["BEST_AVG_P2P"][0] = p2p
            self.stats["BEST_AVG_P2P"].sort()
            sample_num = len(os.listdir(f"{self.path}/logs/{self.run_name}/samples"))
            # Saves code from good samples
            with open(f"{self.path}/logs/{self.run_name}/samples/sample{sample_num}_{p2p}", "w") as f:
                f.write(response)

    def update(self, results, responses):
        for i, r in enumerate(results):
            self.update_flags(r["flags"])
            self.update_p2p(r["avg_p2p"], responses[i])
            self.stats["TOTAL"] += 1
        if (self.save_snippets): self.update_csv(responses, results)
        if (self.verbose): self.print_verbose()
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(f"{self.path}/logs/{self.run_name}/stats", "w") as f:
                f.write(f"Start Time: {self.start_time}\nLast Updated: {time}\nStats:{self.stats}")