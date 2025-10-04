import os
import json
import pandas as pd
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import requests

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

# PLANO B: Nosso "Motor de Emergência" em português
def run_fallback_system(problem_text, solutions_df):
    print("WARNING: External APIs failed. Activating Fallback System.")
    problem_text_lower = problem_text.lower()
    best_match = None
    highest_score = 0
    
    for index, solution in solutions_df.iterrows():
        score = 0
        for keyword in solution.get('Keywords', []):
            if keyword in problem_text_lower:
                score += 1
        
        if score > highest_score:
            highest_score = score
            best_match = solution
            
    if best_match is not None:
        title = best_match['Solution_Title']
        details = best_match.get('Solution_Details_PT', 'Detalhes não disponíveis.')
        ai_answer = f"Com base no seu relato, uma solução potencial é a **{title}**. \n\n**Detalhes:** {details} \n\n*(Esta é uma análise preliminar baseada em palavras-chave. Para uma sugestão mais detalhada, por favor, tente novamente mais tarde.)*"
    else:
        ai_answer = "Recebemos seu relato, mas não conseguimos determinar uma solução específica no momento. Nossa equipe irá analisá-lo manually. Agradecemos sua contribuição."
        
    return ai_answer

# Classe principal que a Vercel vai usar
class handler(BaseHTTPRequestHandler):

    # MÉTODO PARA RESPONDER ÀS PERGUNTAS DE PERMISSÃO (CORS)
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    # MÉTODO PARA PROCESSAR O PEDIDO DA IA
    def do_POST(self):
        user_problem_text = ""
        try:
            # PLANO A: Tentar usar as IAs externas de alta qualidade
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
            
            # =================================================================
            # <<< PROMPT REFINADO PARA UMA RESPOSTA MAIS CRIATIVA >>>
            # =================================================================
            final_prompt = f"""
            Atue como a IA "Aurora", uma urbanista virtual especialista em soluções sustentáveis. Sua personalidade é otimista, didática e inspiradora.
            
            **Contexto:**
            Um cidadão preocupado relatou o seguinte problema em sua cidade: "{user_problem_text}".
            Sua análise inicial identificou a questão principal como sendo relacionada a: '{best_solution['Solution_Title']}'.

            **Sua Missão:**
            Gerar uma resposta original e encorajadora em **português do Brasil**. Você deve usar os "Dados Técnicos" abaixo como sua base de conhecimento, mas **NÃO DEVE simplesmente copiar ou parafrasear o texto**.

            **Instruções para a Resposta:**
            1.  **Síntese e Criatividade:** Elabore uma explicação coesa e autoral sobre a solução. Use os dados técnicos como inspiração para explicar o conceito, o porquê ele funciona e seus benefícios.
            2.  **Adicione Valor:** Enriqueça a explicação. Dê um exemplo prático de como a solução poderia ser vista na cidade do usuário (ex: "Imagine se aquela praça de cimento perto da sua casa se transformasse em um 'parque de bolso'...")
            3.  **Linguagem Acessível:** Traduza qualquer termo técnico para uma linguagem que qualquer cidadão possa entender.
            4.  **Estrutura Clara:** Siga a estrutura: Saudação empática -> Explicação da Solução (sua parte criativa) -> Sugestão de um próximo passo prático -> Mensagem final inspiradora.

            **Dados Técnicos (Base de Conhecimento para sua inspiração):**
            - Título da Solução: {best_solution['Solution_Title']}
            - Detalhes: {best_solution.get('Solution_Details_PT', 'Não há detalhes técnicos disponíveis.')}
            """
            generation_model = genai.GenerativeModel('gemini-pro')
            final_response = generation_model.generate_content(final_prompt)
            ai_answer = final_response.text

        except Exception as e:
            # SE QUALQUER COISA NO PLANO A FALHAR, EXECUTE O PLANO B
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