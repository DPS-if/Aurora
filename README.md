# Projeto UrbanMinds - NASA Space Apps Challenge

**Desafio:** Data Pathways to Healthy Cities and Human Settlements

**UrbanMinds** é uma plataforma de visualização de dados geoespaciais projetada para permitir a qualquer pessoa—de planejadores urbanos a cidadãos curiosos—explorar indicadores ambientais em qualquer cidade do mundo. Utilizando dados em tempo real do serviço **NASA GIBS (Global Imagery Browse Services)**, a ferramenta oferece uma visão clara sobre a saúde urbana sem a necessidade de descarregar ou processar dados complexos.

## Indicadores Analisados

A plataforma foca em três questões críticas para a qualidade de vida urbana, com dados globais e atualizados da NASA:

1.  **Ilhas de Calor:** Visualização da Temperatura de Superfície (LST).
2.  **Poluição do Ar:** Análise da concentração de Dióxido de Nitrogénio (NO₂).
3.  **Saúde da Vegetação:** Exploração do Índice de Vegetação (NDVI).

## Arquitetura da Solução (Frontend-Driven)

A nova arquitetura é extremamente leve e robusta:

- **Backend:** Um micro-servidor **Flask** (Python) com uma única função: servir a página web principal (`index.html`).
- **Frontend:** O coração da aplicação. Uma página única (SPA) construída com **HTML, TailwindCSS e JavaScript**.
- **Mapa Interativo:** **Leaflet.js** é usado para a visualização.
- **Pesquisa de Cidades:** A biblioteca **Leaflet Control Geocoder** com o provedor Nominatim (baseado em OpenStreetMap) permite a pesquisa de qualquer localidade.
- **Dados da NASA:** Os dados não são descarregados. São consumidos em tempo real através do protocolo **WMS (Web Map Service)** do serviço **NASA GIBS**. Isto elimina a necessidade de scripts de download, processamento de dados e resolve permanentemente os erros de links quebrados.

## Como Executar o Projeto

### Pré-requisitos
- Python 3.8+
- pip (gestor de pacotes do Python)

### 1. Configurar o Ambiente

```bash
# Clone o repositório e entre na pasta
git clone <url-do-seu-repositorio>
cd urbanminds

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate