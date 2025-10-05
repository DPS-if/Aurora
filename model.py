from transformers import pipeline

# Carrega o modelo LLaMA 2 (ou outro open source)
gerador = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf")

def gerar_solucao(prompt):
    entrada = f"Proponha uma solução para o seguinte problema ambiental: {prompt}"
    resposta = gerador(entrada, max_length=200, do_sample=True)[0]['generated_text']
    return resposta
