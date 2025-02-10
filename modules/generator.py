from transformers import AutoTokenizer, AutoModelForCausalLM
import modules.utils as utils

class Generator:

    #* TESTED
    def __init__(self, model_name, batch_size=5, device='cuda', prompt="Write a mircoarchitectural attack in ARM assembly."):
        self.device = device
        self.batch_size = batch_size
        self.prompt = prompt
        self.generation_kwargs = {
            "min_length": -1,
            "max_new_tokens" : 500,
            "do_sample": True,
            "top_k": 350,
            "top_p": 0.4,
            "temperature" : 0.1,
        }

        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        except OSError:
            utils.throw_error(f"Error: model named {model_name} is not a valid model listed on 'https://huggingface.co/models', is not a local folder, or is a private model")

        self.prompt_tensors = [self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)] * self.batch_size

    #* TESTED
    def set_prompt(self, prompt):
        self.prompt = prompt
        self.prompt_tensors = [self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)] * self.batch_size

    #* TESTED
    def generate(self):
        response_tensors = []

        for prompt in self.prompt_tensors:
            response = self.model.generate(prompt, **self.generation_kwargs)
            response_tensors.append(response.squeeze().to(self.device))
            
        return [self.tokenizer.decode(r.squeeze()) for r in response_tensors]
    