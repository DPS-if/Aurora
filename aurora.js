// aurora.js
// Chamado APENAS pelo index.html
// Lógica de comunicação com a API Serverless

document.addEventListener('DOMContentLoaded', function () {
    
    // O endpoint da sua função serverless, mapeado para api/aurora-resolution.js
    const API_ENDPOINT = '/api/aurora-resolution'; 

    async function runAuroraAnalysis(event) {
        event.preventDefault(); // Impede o envio de formulário HTML padrão

        const locationInput = document.getElementById('location');
        const issueInput = document.getElementById('issue');
        const resolutionOutput = document.getElementById('resolution');
        const sendButton = document.getElementById('send-analysis-button');
        
        if (!locationInput || !issueInput || !resolutionOutput) {
            console.error("ERRO: Elementos da seção Aurora não encontrados (Verifique o index.html).");
            return;
        }

        const locationValue = locationInput.value.trim();
        const issueValue = issueInput.value.trim();
        
        if (!locationValue || !issueValue) {
            resolutionOutput.value = "Por favor, preencha a cidade/localização e a questão para a análise.";
            return;
        }

        // 1. Estado de Carregamento
        const originalButtonText = sendButton.textContent;
        sendButton.disabled = true;
        sendButton.textContent = 'Analisando...';
        resolutionOutput.value = `Aurora está analisando a questão de '${locationValue}'... Por favor, aguarde a resposta da IA.`;

        // Constrói o Prompt completo para enviar à Groq
        const prompt = `Localização: ${locationValue}. Problema: ${issueValue}`;

        try {
            // 2. Faz a chamada assíncrona (fetch) para a Serverless Function
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt }),
            });

            if (!response.ok) {
                // Trata erros de HTTP
                const errorData = await response.json().catch(() => ({ error: 'Erro de rede ou servidor desconhecido.' }));
                throw new Error(errorData.error || `Erro de rede ou servidor: Código ${response.status}`);
            }

            const data = await response.json();
            
            // 3. Exibe o resultado da IA
            // O campo 'response' vem do seu aurora-resolution.js
            const finalResolution = data.response || "A Aurora não retornou uma análise válida.";
            resolutionOutput.value = finalResolution;

        } catch (error) {
            console.error("Erro na Análise da Aurora:", error);
            resolutionOutput.value = `ERRO: Não foi possível obter a análise da Aurora. Por favor, tente novamente. Detalhes: ${error.message}`;
        } finally {
            // 4. Restaura o estado do botão
            sendButton.disabled = false;
            sendButton.textContent = originalButtonText;
        }
    }

    // Conecta o botão "SEND!"
    const sendButton = document.getElementById('send-analysis-button');
    if (sendButton) {
        sendButton.addEventListener('click', runAuroraAnalysis);
    } else {
        console.warn("AVISO: O botão 'SEND!' da Aurora não foi encontrado.");
    }
});