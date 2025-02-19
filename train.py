import torch
from tqdm import tqdm
from transformers import AutoTokenizer
from trl import AutoModelForCausalLMWithValueHead, PPOConfig, PPOTrainer
from modules.classifier import Classifier

def get_reward(result):
    
    return

if __name__ == "__main__":
    # Adjustable Hyperparams
    device = 'cuda'
    batch_size = 128
    epochs = 500
    query_txt = "Write a mircoarchitectural attack in ARM assembly."
    new_model_name = "AutoMAD-RL-3"

    config = PPOConfig(
        model_name="reddest-panda/AutoMAD-small",
        learning_rate=1.41e-5,
        optimize_cuda_cache= True,
        mini_batch_size=2,
        batch_size=batch_size,
        log_with="wandb"
    )

    generation_kwargs = {
        "min_length": -1,
        "max_new_tokens" : 500,
        "do_sample": True,
        "top_k": 350,
        "top_p": 0.4,
        "temperature" : 0.1,
    }

    # Init PPO Trainer
    model = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)
    ref_model = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    tokenizer.pad_token = tokenizer.eos_token

    optimizer = torch.optim.SGD(model.parameters(), lr=config.learning_rate)
    lr_scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9)

    ppo_trainer = PPOTrainer(config, model, ref_model, tokenizer, optimizer=optimizer, lr_scheduler=lr_scheduler)

    # Init Classifier, used to run code on arm device
    classifier = Classifier("arm/pwr_template.c", "configs/measure.xml")
    
    query_tensors = [tokenizer.encode(query_txt, return_tensors="pt").squeeze().to(device)] * batch_size
    batch = {
        "query" : [query_txt] * batch_size,
        "response" : [],
    }

    # Training Loop
    for epoch in tqdm(range(epochs), "epoch: "):
        #### Get response from model
        response_tensors = []
        for query in query_tensors:
            response = ppo_trainer.generate(query, **generation_kwargs)
            response_tensors.append(response.squeeze().to(device))
        batch['response'] = [tokenizer.decode(r.squeeze()) for r in response_tensors]

        #### Compute reward
        results = [classifier.get_results(r) for r in batch['response']]
        rewards = [torch.tensor(get_reward(r), device=device, dtype=torch.float32) for r in results]

        #### Run PPO step
        try:
            stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
            ppo_trainer.log_stats(stats, batch, rewards)
            model.push_to_hub(new_model_name)
        except Exception:
            continue