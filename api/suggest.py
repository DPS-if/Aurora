import os
import flask
import google.generativeai as genai
import json

app = flask.Flask(__name__)

# Carrega base de conhecimento
with open("data/knowledge_base.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)

# Configura Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def gerar_resposta(problem):
    # Gera contexto com base nos snippets
    contexto = "\n".join([
        f"{item['keyword']}: {item['snippet']}"
        for item in knowledge_base
    ])
    prompt = (
        f"Baseado no seguinte contexto:\n{contexto}\n\n"
        f"Qual seria uma solução para o problema: \"{problem}\"?"
    )
    response = model.generate_content(prompt)
    return response.text

@app.route("/api/suggest", methods=["POST"])
def suggest():
    data = flask.request.get_json()
    problem = data.get("problem", "")
    resposta = gerar_resposta(problem)
    return flask.jsonify({"solution": resposta})

if __name__ == "__main__":
    app.run()
