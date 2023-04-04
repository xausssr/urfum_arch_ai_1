import codecs
import datetime
import os
from hashlib import sha256

import torch
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response, render_template, request
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import DEBUG, DELETE_TIMEOUT, INFERENCE_TIMEOUT, DEVICE, HOST

# initialisation of server
if not os.path.exists("./cache"):
    os.mkdir("./cache")

if not os.path.exists("./cache/cpu_available"):
    codecs.open("./cache/cpu_available", "w", "utf-8").write("y")


# init insatance for model
def __init_model():
    model_name = "IlyaGusev/rugpt3medium_sum_gazeta"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(DEVICE)
    return model, tokenizer


QUEUE = dict()


def predict(result_id: str) -> None:
    """Predict summary from given text

    Args:
        text (str): input news text
        result_id (str): result_id of user
    """
    cpu_available = codecs.open("./cache/cpu_available", "r").read()
    if cpu_available == "n":
        return None
    if f"{result_id}_result" in os.listdir("./cache"):
        return None
    if DEBUG:
        print(f"compute for id: {result_id}")
    codecs.open("./cache/cpu_available", "w", "utf-8").write("n")
    text = codecs.open(f"./cache/{result_id}", "r", "utf-8").read()
    if DEBUG:
        print(f"start for {result_id}")
    model, tokinezer = __init_model()
    text_tokens = tokinezer(
        text,
        max_length=600,
        add_special_tokens=False,
        padding=False,
        truncation=True
    )["input_ids"]
    input_ids = text_tokens + [tokinezer.sep_token_id]
    input_ids = torch.LongTensor([input_ids]).to(DEVICE)
    output_ids = model.generate(
        input_ids=input_ids,
        no_repeat_ngram_size=4
    )
    cpu_available = True

    summary = tokinezer.decode(output_ids[0], skip_special_tokens=False)
    summary = summary.split(tokinezer.sep_token)[1]
    summary = summary.split(tokinezer.eos_token)[0]
    codecs.open(f"./cache/{result_id}_result", "w", "utf-8").write(summary)
    codecs.open("./cache/cpu_available", "w", "utf-8").write("y")

    if DEBUG:
        print(f"complete for {result_id}")


def get_next_id():
    if len(QUEUE) > 0:
        if DEBUG:
            print("get new id...")
        ids = [x for x in QUEUE.keys()]
        if len(ids) > 0:
            predict(ids[0])

      
def clear_results():
    for n in os.listdir("./cache/"):
        if n != "cpu_available" and "_result" not in n:
            now = datetime.datetime.now()
            if now - QUEUE[n] > datetime.timedelta(minutes=DELETE_TIMEOUT):
                del QUEUE[n]
                os.remove(f"./cache/{n}_result")
                os.remove(f"./cache/{n}")
                if DEBUG:
                    print(f"delete for {n}, cause: timeout")


# next id to predict
NEXT_ID = None
# Allready compute flag
# run predictions on backgroud
scheduler = BackgroundScheduler()
scheduler.add_job(func=get_next_id, trigger="interval", seconds=INFERENCE_TIMEOUT)
scheduler.start()


app = Flask("summator")
# fix to russian symbols
app.config['JSON_AS_ASCII'] = False


@app.route("/")
def main_page():
    return render_template("main.html")


# dev page for curl
@app.route("/send_text", methods=["POST"])
def send_text():
    """API endpoint to proccess text from cli. Need to send raw text in POST"""
    clear_results()
    if request.method == 'POST':
        data = request.data.decode("utf-8")
        result_id = sha256(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f').encode('utf-8')).hexdigest()
        QUEUE[result_id] = datetime.datetime.now()
        codecs.open(f"./cache/{result_id}", "w", "utf-8").write(data)
        return Response(result_id, status=200)
    else:
        return Response("Non-valid request", status=400)


@app.route("/get_result", methods=["GET"])
def get_results():
    """API endpoint to get results of model apply"""

    if request.args.get('id'):
        result_id = request.args.get('id')
        if result_id not in QUEUE:
            return Response(f"No results for {result_id}, may be clean by timer? try one more time", status=410)
        if f"{result_id}_result" in os.listdir("./cache"):
            result = codecs.open(f"./cache/{result_id}_result", "r", "utf-8").read()
            del QUEUE[result_id]
            os.remove(f"./cache/{result_id}_result")
            os.remove(f"./cache/{result_id}")
            if DEBUG:
                print(f"delete for {result_id}, cause: user get result")
            return Response(result, status=200)
        else:
            clear_results()
            return Response("You text is not processed, please wait", status=204)
    else:
        clear_results()
        return Response("Add parameter 'id'", status=400)


if __name__ == '__main__':
    app.run(host=HOST, debug=False)
