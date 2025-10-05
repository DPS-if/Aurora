from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
modelo = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf")

@app.route("/api/suggest", methods=["POST"])
def sugerir():
    dados = request.get_json()
    prompt = dados.get("problem_text", "")
    resposta = modelo(prompt, max_length=300, do_sample=True)[0]['generated_text']
    return jsonify({"solution": resposta})
