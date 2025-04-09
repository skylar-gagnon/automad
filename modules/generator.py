import os
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
from trl import OnlineDPOConfig, OnlineDPOTrainer, BasePairwiseJudge # type: ignore
from modules.utils import SSHError
from math import log2
from datasets import load_dataset

class AttackJudge(BasePairwiseJudge):
    def __init__(self, classifier, logger):
        super().__init__()
        self.classifier = classifier
        self.logger = logger

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
            better_option = 0
        return better_option

    def check_status(self):
        failed_attempts = self.logger.stats["SSH_FAIL"]
        if failed_attempts > 5:
            raise SSHError(f"SSH is failing, exiting with {failed_attempts} SSH failed attempts.")

    def judge(self, prompts, completions, shuffle_order=False):
        choices = []
        for completion in completions:
            results = [self.classifier.get_result(option) for option in completion]
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

class Generator:
    #* TESTED
    def __init__(self,
                 path,
                 model_name="reddest-panda/AutoMAD-RL-3",
                 batch_size=2,
                 device='cuda',
                 prompt="Write a program in ARM assembly that performs a microarchitectural attack.\nmain:\n\t.cfi_startproc\n",
                 model_kwargs={
                     "min_length": -1,
                     "max_new_tokens" : 250,
                     "do_sample": True,
                     "top_k": 500,
                     "temperature" : 0.9,
                     }
                ):
        self.path = path
        self.device = device
        self.batch_size = batch_size
        self.prompt = prompt
        self.model_kwargs = model_kwargs

        self.model = AutoModelForCausalLM.from_pretrained(model_name, low_cpu_mem_usage=True)
        self.model.to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.prompt_tensors = [self.tokenizer(prompt, return_tensors="pt").to(self.device)] * self.batch_size

    #* TESTED
    def set_prompt(self, prompt):
        self.prompt = prompt
        self.prompt_tensors = [self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)] * self.batch_size

    def make_dataset(self, size):
        os.makedirs(f"{self.path}/data", exist_ok=True)
        ds = pd.DataFrame({
            "prompt" : [{
                "content" : self.prompt,
                "role" : "user",
                        }]
        })
        for _ in range(int(log2(size))):
            ds = pd.concat([ds, ds], ignore_index=True)
        
        ds.reindex()
        ds.to_csv(f"{self.path}/data/prompts.csv")
    
    #* TESTED
    def generate(self):
        response_tensors = []

        for prompt in self.prompt_tensors:
            response = self.model.generate(**prompt, pad_token_id=self.tokenizer.eos_token_id, **self.model_kwargs)
            response_tensors.append(response.squeeze().to(self.device))
            
        return [self.tokenizer.decode(r.squeeze()) for r in response_tensors]
    
    def train(self,
              classifier,
              logger,
              save_model_name="reddest-panda/AutoMAD-debug",
              train_model_name="reddest-panda/AutoMAD-RL-2",
              ref_model_name="reddest-panda/AutoMAD-small",
              make_dataset=True,
              dataset_size=32000,
              dataset_path="data/prompts.csv",
              push_to_hub=False,
              log_training=False,
              epochs=6
              ):
        output_dir = save_model_name.split("/")[-1]
        if (make_dataset):
            self.make_dataset(dataset_size)
            train_dataset = load_dataset("csv", data_files=f"{self.path}/data/prompts.csv", split="train")
        else:
            train_dataset = load_dataset("csv", data_files=dataset_path, split="train")

        if log_training:
            report_to = "wandb"
        else:
            report_to = "none"

        model = AutoModelForCausalLM.from_pretrained(train_model_name, low_cpu_mem_usage=True)
        ref_model = AutoModelForCausalLM.from_pretrained(ref_model_name, low_cpu_mem_usage=True)
        tokenizer = AutoTokenizer.from_pretrained(train_model_name)
        judge = AttackJudge(classifier, logger)
        training_args = OnlineDPOConfig(output_dir=output_dir, logging_steps=10, per_device_train_batch_size=4, push_to_hub=push_to_hub, hub_strategy='checkpoint', gradient_accumulation_steps=2, max_new_tokens=250, max_length=300, num_train_epochs=epochs, report_to=report_to)

        trainer = OnlineDPOTrainer(
            model=model,ref_model=ref_model, judge=judge, args=training_args, processing_class=tokenizer, train_dataset=train_dataset
        )

        model.enable_input_require_grads()
        trainer.train()
        if (push_to_hub) : trainer.push_to_hub(save_model_name)