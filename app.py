import torch
from flask import Flask, render_template, request
from transformers import AutoModelForCausalLM, AutoTokenizer


# init insatance for model
def __init_model():

    model_name = "IlyaGusev/rugpt3medium_sum_gazeta"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to("cpu")
    return model, tokenizer

#TODO hold instance, not sure, that clear way in Flask, need tests
MODEL, TOKINIZER = __init_model()

def predict(text: str) -> str:
    """Predict summary from given text

    Args:
        text (str): input news text

    Returns:
        str: summary
    """
    text = request.data.decode("utf8")
    print(text)
    text_tokens = TOKINIZER(
        text,
        max_length=600,
        add_special_tokens=False, 
        padding=False,
        truncation=True
    )["input_ids"]
    input_ids = text_tokens + [TOKINIZER.sep_token_id]
    input_ids = torch.LongTensor([input_ids]).to("cpu")

    output_ids = MODEL.generate(
        input_ids=input_ids,
        no_repeat_ngram_size=4
    )

    summary = TOKINIZER.decode(output_ids[0], skip_special_tokens=False)
    summary = summary.split(TOKINIZER.sep_token)[1]
    summary = summary.split(TOKINIZER.eos_token)[0]
    return summary


app = Flask(__name__)
# fix to russian symbols
app.config['JSON_AS_ASCII'] = False

@app.route("/")
def main_page():
    return render_template("main.html")

# dev page for curl
@app.route("/api", methods=["POST"])
def dev_page():
    """API endpoint to proccess text from cli. Need to send raw text in POST"""
    if request.method == 'POST':
        data = request.data.decode("utf-8")
        summary = predict(data)
        return summary
    else:
        return "Non-valid request"

