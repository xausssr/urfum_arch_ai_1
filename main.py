import argparse
import os
import warnings

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# global settings to script
warnings.filterwarnings("ignore", category=UserWarning)
PATH = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(
    prog = 'AI Text Annotation',
    description = 'Annotate (summarize) russian news post',
    epilog = 'You need GPU with at least 8 GB, by default inference on CPU'
)

parser.add_argument('--file', help="absolute path to file with text (*.txt in cp-1251)", required=False)
parser.add_argument("--device", help="device for inference in torch notation (cuda:0, cuda:1)", default="cpu")

args = parser.parse_args()

if args.file is None:
    print("Use default text")
    with open(os.path.join(PATH, "default_text.txt"), "r") as f:
        article_text = f.read()
else:
    print(f"Use text from {args.file}")
    with open(args.file, "r", encoding="utf-8") as f:
        article_text = f.read()

print(f"Use {args.device} device for inference")

model_name = "IlyaGusev/rugpt3medium_sum_gazeta"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to(args.device)

text_tokens = tokenizer(
    article_text,
    max_length=600,
    add_special_tokens=False, 
    padding=False,
    truncation=True
)["input_ids"]
input_ids = text_tokens + [tokenizer.sep_token_id]
input_ids = torch.LongTensor([input_ids]).to(args.device)

output_ids = model.generate(
    input_ids=input_ids,
    no_repeat_ngram_size=4
)

summary = tokenizer.decode(output_ids[0], skip_special_tokens=False)
summary = summary.split(tokenizer.sep_token)[1]
summary = summary.split(tokenizer.eos_token)[0]
print(f"Article summary:\n{summary}")
