import os
import json
import pandas as pd
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import requests

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

# PLANO B: "Motor de Emergência" (continua o mesmo)
def run_fallback_system(problem_text, solutions_df):
    print("WARNING: External APIs failed. Activating Fallback System.")
    # (O código do Plano B continua exatamente o mesmo de antes, sem alterações)
    problem_text_lower = problem_text.lower()
    best_match = None
    highest_score = 0
    for index, solution in solutions_df.iterrows():
        score = 0
        for keyword in solution.get('Keywords', '').split(','):
            if keyword.strip() in problem_text_lower:
                score += 1
        if score > highest_score:
            highest_score = score
            best_match = solution
    if best_match is not None:
        title = best_match['Solution_Title']
        details = best_match.get('Source_Text', 'Detalhes não disponíveis.')
        source = best_match.get('Source_Name', 'Fonte não especificada.')
        ai_answer = f"Com base no seu relato, uma solução potencial é a **{title}**. \n\n**Análise Preliminar:** {details} \n\n__{source}__ \n\n*(Esta é uma análise baseada em palavras-chave.)*"
    else:
        ai_answer = "Recebemos o seu relato, mas não conseguimos determinar uma solução específica neste momento. A nossa equipa irá analisá-lo manualmente. Agradecemos a sua contribuição."
    return ai_answer

# Classe principal que a Vercel vai usar
class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_POST(self):
        user_problem_text = ""
        try:
            # --- ETAPA 1: RECEBER O PROBLEMA DO USUÁRIO ---
            print("INFO: Initiating AI Chain.")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            user_problem_text = user_input.get('problem_text', '')

            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            HF_TOKEN = os.environ.get('HUGGING_FACE_TOKEN')
            
            if not GEMINI_API_KEY or not HF_TOKEN:
                raise ValueError("API keys are not configured in Vercel.")
                
            genai.configure(api_key=GEMINI_API_KEY)
            
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            solutions_df = pd.DataFrame(solutions_data)
            
            # --- MODELO 1: O CLASSIFICADOR (Hugging Face) ---
            print("INFO: Model 1 (Classifier) is running...")
            problem_labels = solutions_df['Problem_Tags'].tolist()
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = { "inputs": user_problem_text, "parameters": {"candidate_labels": problem_labels} }
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            classification_result = response.json()
            detected_problem_tag = classification_result['labels'][0]
            print(f"✅ Model 1 Result: {detected_problem_tag}")
            
            best_solution = solutions_df[solutions_df['Problem_Tags'] == detected_problem_tag].iloc[0]

            # --- MODELO 2: O ESTRATEGISTA (Gemini para "Turbinar" o Prompt) ---
            print("INFO: Model 2 (Strategist) is running...")
            expansion_prompt = f"""
            Você é um urbanista especialista e estrategista. Sua tarefa é pegar a reclamação simples de um cidadão e expandi-la para um prompt de análise técnica detalhado.

            Reclamação do Cidadão: "{user_problem_text}"
            Tema Principal Identificado: "{best_solution['Solution_Title']}"

            Expanda a reclamação adicionando os seguintes elementos:
            1.  **Jargão Técnico:** Introduza termos técnicos relevantes (ex: 'pegada ecológica', 'resiliência climática', 'gentrificação', 'mobilidade ativa').
            2.  **Perguntas-Chave:** Formule 2-3 perguntas complexas que um especialista faria para aprofundar a análise do problema.
            3.  **Conceitos Relacionados:** Liste 3-4 conceitos de planeamento urbano que se conectam ao problema.
            
            Gere apenas o texto expandido, sem introduções.
            """
            expansion_model = genai.GenerativeModel('gemini-pro')
            expansion_response = expansion_model.generate_content(expansion_prompt)
            enriched_prompt = expansion_response.text
            print(f"✅ Model 2 Result: Enriched prompt created successfully.")

            # --- MODELO 3: O REDATOR-CHEFE (Gemini para a Resposta Final) ---
            print("INFO: Model 3 (Chief Editor) is running...")
            final_prompt = f"""
            Atue como a IA "Aurora", uma urbanista virtual de renome. Sua personalidade é analítica, profunda e articulada.

            **Missão:**
            Gerar uma resposta técnica, explicativa e complexa para um cidadão, usando três fontes de informação: a reclamação original, um prompt técnico expandido e um texto-base de uma fonte de conhecimento.

            **Fonte 1: Reclamação Original do Cidadão:**
            "{user_problem_text}"

            **Fonte 2: Análise Técnica Expandida (para guiar o seu raciocínio):**
            "{enriched_prompt}"

            **Fonte 3: Texto-Base de Conhecimento (base para a solução):**
            - Título da Solução: {best_solution['Solution_Title']}
            - Fonte: {best_solution['Source_Name']}
            - Texto: {best_solution.get('Source_Text')}

            **Instruções para a Resposta Final (em português do Brasil):**
            1.  **Estrutura:** Organize a sua resposta em secções claras: "Introdução ao Problema", "Análise Técnica Aprofundada" e "Caminhos para a Solução".
            2.  **Profundidade:** Na "Análise Técnica", use os conceitos do prompt expandido (Fonte 2) para detalhar as complexidades do problema.
            3.  **Fundamentação:** Na secção "Caminhos para a Solução", formule a sua recomendação com base nas informações do Texto-Base (Fonte 3). Não copie o texto, use-o para fundamentar a sua proposta.
            4.  **Citação:** No final da resposta, cite a fonte principal: "Análise baseada em: {best_solution['Source_Name']}".
            """
            final_model = genai.GenerativeModel('gemini-pro')
            final_response = final_model.generate_content(final_prompt)
            ai_answer = final_response.text

        except Exception as e:
            # SE QUALQUER ETAPA DO PLANO A FALHAR, EXECUTE O PLANO B
            print(f"ERROR in Plan A: {e}")
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            solutions_df = pd.DataFrame(solutions_data)
            ai_answer = run_fallback_system(user_problem_text, solutions_df)

        # Envia a resposta final
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps({'solution': ai_answer})
        self.wfile.write(response.encode('utf-8'))
        return