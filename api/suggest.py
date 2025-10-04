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
    problem_text_lower = problem_text.lower()
    best_match = None
    highest_score = 0
    
    for index, solution in solutions_df.iterrows():
        score = 0
        keywords_list = [kw.strip() for kw in solution.get('Keywords', '').split(',')]
        for keyword in keywords_list:
            if keyword in problem_text_lower:
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
        ai_answer = ""
        try:
            # --- ETAPA 1: RECEBER O PROBLEMA DO UTILIZADOR ---
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

            # --- CORREÇÃO IMPORTANTE E VERIFICAÇÃO DE SEGURANÇA ---
            matching_solutions = solutions_df[solutions_df['Problem_Tags'] == detected_problem_tag]
            if matching_solutions.empty:
                print(f"ERROR: No match found for tag '{detected_problem_tag}'. Activating fallback.")
                raise ValueError(f"Classifier tag '{detected_problem_tag}' not found in solutions.json")
            
            best_solution = matching_solutions.iloc[0]
            
            # --- MODELO 2: O ESTRATEGISTA ---
            print("INFO: Model 2 (Strategist) is running...")
            expansion_prompt = f"""Expanda a reclamação de um cidadão '{user_problem_text}' sobre '{best_solution['Solution_Title']}' num prompt técnico, adicionando jargões, perguntas-chave e conceitos de planeamento urbano relacionados."""
            expansion_model = genai.GenerativeModel('gemini-pro')
            expansion_response = expansion_model.generate_content(expansion_prompt)
            enriched_prompt = expansion_response.text
            print(f"✅ Model 2 Result: Enriched prompt created.")

            # --- MODELO 3: O REDATOR-CHEFE ---
            print("INFO: Model 3 (Chief Editor) is running...")
            draft_prompt = f"""Atue como a IA "Aurora". Gere uma resposta técnica e complexa para a reclamação de um cidadão, usando as informações abaixo.
            Reclamação Original: "{user_problem_text}"
            Análise Técnica Expandida: "{enriched_prompt}"
            Texto-Base de Conhecimento: "{best_solution.get('Source_Text')}"
            Instruções: Organize em secções ("Introdução", "Análise Aprofundada", "Soluções"). Fundamente as soluções no Texto-Base."""
            draft_model = genai.GenerativeModel('gemini-pro')
            draft_response = draft_model.generate_content(draft_prompt)
            first_draft = draft_response.text
            print(f"✅ Model 3 Result: First draft created.")

            # --- MODELO 4: O CRÍTICO DE QUALIDADE ---
            print("INFO: Model 4 (Quality Critic) is running...")
            critique_prompt = f"""Analise a 'Primeira Versão da Resposta' para ver se ela responde diretamente à 'Reclamação Original do Cidadão'.
            Reclamação Original: "{user_problem_text}"
            Primeira Versão: "{first_draft}"
            Se for boa, responda 'APROVADO'. Se não, dê uma instrução curta para a corrigir."""
            critique_model = genai.GenerativeModel('gemini-pro')
            critique_response = critique_model.generate_content(critique_prompt)
            critique_feedback = critique_response.text.strip()
            print(f"✅ Model 4 Result: Feedback is '{critique_feedback}'")

            # --- ETAPA FINAL: REFINAMENTO ---
            if "APROVADO" in critique_feedback:
                print("INFO: Draft approved. Finalizing response.")
                ai_answer = first_draft
                ai_answer += f"\n\n**Análise baseada em:** {best_solution['Source_Name']}"
            else:
                print("INFO: Draft needs refinement. Rerunning Chief Editor...")
                refinement_prompt = f"""Reescreva a sua 'Primeira Versão' para atender ao seguinte feedback do revisor: '{critique_feedback}'.
                Primeira Versão (para corrigir): "{first_draft}"
                Reclamação Original (para referência): "{user_problem_text}" """
                refinement_model = genai.GenerativeModel('gemini-pro')
                final_response = refinement_model.generate_content(refinement_prompt)
                ai_answer = final_response.text
                ai_answer += f"\n\n**Análise baseada em:** {best_solution['Source_Name']}"

        except Exception as e:
            print(f"ERROR in Plan A: {e}")
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            solutions_df = pd.DataFrame(solutions_data)
            ai_answer = run_fallback_system(user_problem_text, solutions_df)

        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps({'solution': ai_answer})
        self.wfile.write(response.encode('utf-8'))
        return