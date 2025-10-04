import os
import json
import pandas as pd
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import requests

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

# PLANO B: "Motor de Emergência" que também cita a fonte
def run_fallback_system(problem_text, solutions_df):
    print("WARNING: External APIs failed. Activating Fallback System.")
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
        ai_answer = f"Com base no seu relato, uma solução potencial é a **{title}**. \n\n**Análise Preliminar:** {details} \n\n__{source}__ \n\n*(Esta é uma análise baseada em palavras-chave. Para uma sugestão mais detalhada, por favor, tente novamente mais tarde.)*"
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
        ai_answer = ""
        try:
            # PLANO A: Usar as IAs para raciocinar com base na fonte
            print("INFO: Initiating Plan A with external APIs.")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            user_problem_text = user_input.get('problem_text', '')

            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            HF_TOKEN = os.environ.get('HUGGING_FACE_TOKEN')
            
            if not GEMINI_API_KEY or not HF_TOKEN:
                raise ValueError("API keys are not configured in Vercel Environment Variables.")
                
            genai.configure(api_key=GEMINI_API_KEY)
            
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            solutions_df = pd.DataFrame(solutions_data)
            
            print("INFO: Classifying text using Hugging Face Inference API...")
            problem_labels = solutions_df['Problem_Tags'].tolist()
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = { "inputs": user_problem_text, "parameters": {"candidate_labels": problem_labels} }
            
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            classification_result = response.json()
            
            detected_problem = classification_result['labels'][0]
            print(f"✅ [HF API] Problema detectado: {detected_problem}")

            best_solution = solutions_df[solutions_df['Problem_Tags'] == detected_problem].iloc[0]
            
            # <<< PROMPT REFINADO PARA RACIOCINAR E CITAR A FONTE >>>
            final_prompt = f"""
            Atue como a IA "Aurora", uma urbanista virtual especialista. A sua personalidade é didática, precisa e confiável.

            **Contexto:**
            Um cidadão relatou o seguinte problema: "{user_problem_text}".
            A sua análise inicial identificou a questão principal como sendo relacionada a: '{best_solution['Solution_Title']}'.

            **Sua Missão:**
            Gerar uma resposta original e informativa em **português do Brasil**, utilizando **APENAS** as informações contidas no "Texto-Base da Fonte" abaixo.

            **Instruções para a Resposta:**
            1.  **Síntese e Análise:** Leia o Texto-Base e sintetize os pontos mais importantes para explicar a solução ao cidadão. Não copie o texto, reestruture a informação numa explicação clara e coesa.
            2.  **Aplicação Prática:** Conecte a explicação teórica do Texto-Base ao problema do cidadão. Dê um exemplo prático.
            3.  **Citação Obrigatória:** No final da sua resposta, você **DEVE** citar a fonte de onde tirou a informação. Inclua a seguinte linha exatamente como está: "Fonte da Análise: {best_solution['Source_Name']}".

            **Texto-Base da Fonte (Use APENAS esta informação):**
            ---
            {best_solution.get('Source_Text', 'Não há detalhes técnicos disponíveis.')}
            ---
            """
            generation_model = genai.GenerativeModel('gemini-pro')
            final_response = generation_model.generate_content(final_prompt)
            ai_answer = final_response.text

        except Exception as e:
            # SE O PLANO A FALHAR, EXECUTE O PLANO B
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