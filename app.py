import gradio as gr
import requests
import json
import os

# --- Configurações ---
# Usaremos a API de Inferência gratuita da Hugging Face para o Llama 3
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
MODEL_NAME = "Llama 3 (via Hugging Face API)"

# Carrega a nossa base de conhecimento local
try:
    with open('solutions.json', 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)
    knowledge_base_text = json.dumps(knowledge_base, indent=2, ensure_ascii=False)
except FileNotFoundError:
    knowledge_base_text = "ERRO: O ficheiro 'solutions.json' não foi encontrado."

# --- Lógica da IA ---
def get_aurora_response(user_problem, hf_token):
    if not hf_token:
        return "ERRO: O Token de API da Hugging Face não foi fornecido. Por favor, adicione o seu token nos 'Secrets' do seu Space."

    # A personalidade e o prompt que enviaremos para o Llama 3
    system_prompt = "Você é a Aurora, uma IA pesquisadora especialista em mudanças climáticas e desenvolvimento urbano sustentável. Seja sempre simpática, direta e apresente os dados com a confiança de uma académica. Use uma linguagem clara, mas não simplifique excessivamente os conceitos."
    
    # Formato de prompt específico para o Llama 3
    final_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}

**Sua Missão como Pesquisadora:**
Você recebeu um problema de um cidadão e uma base de conhecimento em formato JSON. Siga estas três etapas:

1.  **Identificar o Documento Relevante:** Leia o "Problema do Cidadão" e analise a "Base de Conhecimento" inteira. Identifique qual dos objetos JSON na base de conhecimento é o mais relevante para responder à questão.
2.  **Formular a Resposta:** Use o campo "Texto_Base" do documento que você identificou como a sua única fonte de verdade. Elabore uma resposta aprofundada, original e bem explicada para o cidadão. Não copie o texto, sintetize-o com a sua personalidade de especialista.
3.  **Citar a Fonte:** No final da sua resposta, numa nova linha, cite a fonte usando o campo "Fonte" do documento que você utilizou.

**Base de Conhecimento (Ficheiro JSON):**
{knowledge_base_text}<|eot_id|><|start_header_id|>user<|end_header_id|>

**Problema do Cidadão:**
"{user_problem}"<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": final_prompt,
        "parameters": {
            "max_new_tokens": 512, # Limita o tamanho da resposta
            "temperature": 0.7,    # Controla a criatividade (0.7 é um bom equilíbrio)
            "return_full_text": False,
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # Gera um erro se a resposta não for 'OK'
        result = response.json()
        return result[0]['generated_text']
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com a API da Hugging Face: {str(e)}"

# --- Interface Gráfica com Gradio ---
with gr.Blocks(theme=gr.themes.Soft(), title="Aurora IA") as demo:
    gr.Markdown(
        """
        # 🤖 Aurora IA
        ### Sua pesquisadora especialista em desenvolvimento urbano sustentável.
        Descreva um problema ou faça uma pergunta sobre planeamento urbano, sustentabilidade ou mudanças climáticas para receber uma análise.
        """
    )
    with gr.Row():
        with gr.Column(scale=2):
            problem_input = gr.Textbox(lines=5, label="Problema ou Pergunta", placeholder="Ex: A minha rua fica constantemente alagada quando chove. Que tipo de soluções existem?")
            # O token será lido a partir dos "Secrets" do Space
            # Tentamos obter o token a partir dos segredos do ambiente
            hf_token_secret = os.environ.get('HF_TOKEN')
            submit_button = gr.Button("Analisar com Aurora", variant="primary")
        with gr.Column(scale=3):
            aurora_output = gr.Markdown(label="Análise da Aurora ✨")
    
    gr.Markdown(f"**Modelo em uso:** {MODEL_NAME}")

    submit_button.click(
        fn=lambda problem: get_aurora_response(problem, hf_token_secret),
        inputs=problem_input,
        outputs=aurora_output
    )

if __name__ == "__main__":
    demo.launch()