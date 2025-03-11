import os, random, sys
from modules.utils import notif_failure
from datasets import load_dataset
from trl import OnlineDPOConfig, OnlineDPOTrainer, BasePairwiseJudge
from transformers import AutoModelForCausalLM, AutoTokenizer
from modules.classifier import Classifier
from modules.logger import Logger

class SSHError(Exception):
    pass

class AttackJudge(BasePairwiseJudge):
    def __init__(self, run_name):
        super().__init__()
        self.classifier = Classifier("arm/pwr_template.c", "configs/measure.xml")
        self.logger = Logger(run_name, self.classifier.flags)

    def get_rank(self, flags):
        rankings = {
            "SSH_FAIL"  : 0,
            "COMP_FAIL" : 3,
            "EXEC_FAIL" : 2,
            "PROC_FAIL" : 4,
            "MNTR_FAIL" : 1,
        }
        for key in flags:
            if (flags[key] == 1):
                return rankings[key]
        return 0
    
    def find_better(self, ranks):
        if (ranks[0] < ranks[1]):
            better_option = 0
        elif (ranks[0] > ranks[1]):
            better_option = 1
        else:
            better_option = random.choice([0, 1])
        return better_option

    def check_status(self):
        failed_attempts = self.logger.stats["SSH_FAIL"]
        if failed_attempts > 5:
            raise SSHError(f"SSH is failing, exiting with {failed_attempts} SSH failed attempts.")

    def judge(self, prompts, completions, shuffle_order=False):
        choices = []
        for completion in completions:
            results = [self.classifier.get_results(option) for option in completion]
            self.logger.update(results, completion)

            better_option = 0
            if (results[0]["best_p2p"] > results[1]["best_p2p"]):
                better_option = 0
            elif (results[0]["best_p2p"] < results[1]["best_p2p"]):
                better_option = 1
            else:
                ranks = [self.get_rank(r["flags"]) for r in results]
                better_option = self.find_better(ranks)
            choices.append(better_option)
        self.check_status()
        return choices

def train():
    model_id = "reddest-panda/AutoMAD-RL-2"

    model = AutoModelForCausalLM.from_pretrained(model_id, load_in_8bit=True)
    model.enable_input_require_grads()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    judge = AttackJudge(f"full_run{len(os.listdir('logs'))}")
    train_dataset = load_dataset("csv", data_files="data/prompts.csv", split="train")

    training_args = OnlineDPOConfig(output_dir="AutoMAD-RL-3", max_new_tokens=500, max_length=600, logging_steps=10, auto_find_batch_size=True, num_train_epochs=3)
    trainer = OnlineDPOTrainer(
        model=model, judge=judge, args=training_args, processing_class=tokenizer, train_dataset=train_dataset
    )

    trainer.train()

if __name__ == '__main__':
    try:
        train()
    except:
        notif_failure("RL Phase 2", sys.exc_info(), "configs/email.json")
        exit(1)