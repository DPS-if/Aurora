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
    # ... (código omitido para maior clareza)
    return "Recebemos o seu relato, mas não conseguimos determinar uma solução específica neste momento. A nossa equipa irá analisá-lo manualmente. Agradecemos a sua contribuição."

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
            
            best_solution = solutions_df[solutions_df['Problem_Tags'] == detected_problem_tag].iloc[0]

            # --- MODELO 2: O ESTRATEGISTA (Gemini para "Turbinar" o Prompt) ---
            print("INFO: Model 2 (Strategist) is running...")
            expansion_prompt = f"""Expanda a reclamação de um cidadão '{user_problem_text}' sobre '{best_solution['Solution_Title']}' num prompt técnico, adicionando jargões, perguntas-chave e conceitos de planeamento urbano relacionados."""
            expansion_model = genai.GenerativeModel('gemini-pro')
            expansion_response = expansion_model.generate_content(expansion_prompt)
            enriched_prompt = expansion_response.text
            print(f"✅ Model 2 Result: Enriched prompt created.")

            # --- MODELO 3: O REDATOR-CHEFE (Gemini para a Primeira Versão) ---
            print("INFO: Model 3 (Chief Editor) is running...")
            draft_prompt = f"""
            Atue como a IA "Aurora". Gere uma resposta técnica e complexa para um cidadão.
            Reclamação Original: "{user_problem_text}"
            Análise Técnica Expandida: "{enriched_prompt}"
            Texto-Base de Conhecimento: "{best_solution.get('Source_Text')}"
            Instruções: Organize em secções ("Introdução", "Análise Aprofundada", "Soluções"). Fundamente as soluções no Texto-Base.
            """
            draft_model = genai.GenerativeModel('gemini-pro')
            draft_response = draft_model.generate_content(draft_prompt)
            first_draft = draft_response.text
            print(f"✅ Model 3 Result: First draft created.")

            # --- MODELO 4: O CRÍTICO DE QUALIDADE (Gemini para Revisão) ---
            print("INFO: Model 4 (Quality Critic) is running...")
            critique_prompt = f"""
            Você é um revisor de qualidade de IAs. Analise a "Primeira Versão da Resposta" abaixo.
            O objetivo é garantir que ela responda diretamente e de forma útil à "Reclamação Original do Cidadão".

            Reclamação Original do Cidadão:
            "{user_problem_text}"

            Primeira Versão da Resposta:
            "{first_draft}"

            Sua Tarefa:
            1.  Se a resposta for excelente, clara e diretamente relevante, responda APENAS com a palavra "APROVADO".
            2.  Se a resposta for muito complexa, genérica ou não abordar o ponto central da reclamação, escreva uma instrução curta e direta para o redator-chefe corrigir. Exemplo: "Simplifique a linguagem na secção de análise.", "Foque mais na questão da falta de árvores mencionada pelo cidadão."
            """
            critique_model = genai.GenerativeModel('gemini-pro')
            critique_response = critique_model.generate_content(critique_prompt)
            critique_feedback = critique_response.text.strip()
            print(f"✅ Model 4 Result: Feedback is '{critique_feedback}'")

            # --- ETAPA FINAL: REFINAMENTO (se necessário) ---
            if "APROVADO" in critique_feedback:
                print("INFO: Draft approved. Finalizing response.")
                ai_answer = first_draft
            else:
                print("INFO: Draft needs refinement. Rerunning Chief Editor...")
                refinement_prompt = f"""
                Você é o redator-chefe da IA Aurora. A sua primeira versão de resposta foi devolvida com o seguinte feedback do nosso revisor de qualidade: '{critique_feedback}'.

                Por favor, reescreva a sua resposta para atender a essa crítica. Mantenha a estrutura e a base de conhecimento, mas ajuste o conteúdo conforme a instrução.

                Informações Originais para Referência:
                - Reclamação do Cidadão: "{user_problem_text}"
                - Texto-Base: "{best_solution.get('Source_Text')}"
                - Sua Primeira Versão (para corrigir): "{first_draft}"
                """
                refinement_model = genai.GenerativeModel('gemini-pro')
                final_response = refinement_model.generate_content(refinement_prompt)
                ai_answer = final_response.text
                ai_answer += f"\n\n**Análise baseada em:** {best_solution['Source_Name']}" # Adiciona a citação final

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
        # ... (resto do código de envio da resposta)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps({'solution': ai_answer})
        self.wfile.write(response.encode('utf-8'))
        return