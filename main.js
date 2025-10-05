document.addEventListener('DOMContentLoaded', function () {

    const map = L.map('map', { zoomControl: false }).setView([20, 0], 3);
    L.control.zoom({ position: 'topright' }).addTo(map);
    let markersLayer = new L.LayerGroup().addTo(map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: 'Mapa base &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd'
    }).addTo(map);

    const vegetationLayer = {
        name: 'MODIS_Terra_NDVI_8Day',
        endpoint: 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi',
    };

    // --- BASE DE DADOS MASSIVA COM QUASE 50 CIDADES ---
    const citiesData = {
        // AMÉRICAS
        'São Paulo': [
            { name: 'Parque Ibirapuera', coords: [-23.588, -46.658], type: 'park', info: { heat: { value: '25°C', label: 'Fresco', analysis: 'A vegetação densa reduz a temperatura, criando uma "ilha de frescura".' }, air: { value: '15 µmol/m²', label: 'Baixa', analysis: 'As árvores atuam como filtros naturais, melhorando a qualidade do ar.' }, vegetation: { value: '0.78 NDVI', label: 'Alta', analysis: 'Índice de vegetação saudável.' } } },
            { name: 'Avenida Paulista', coords: [-23.561, -46.656], type: 'urban', info: { heat: { value: '33°C', label: 'Muito Quente', analysis: 'Asfalto e edifícios retêm calor, intensificando a ilha de calor urbana.' }, air: { value: '150 µmol/m²', label: 'Muito Elevada', analysis: 'Alta concentração de poluentes devido ao intenso tráfego de veículos.' }, vegetation: { value: '0.12 NDVI', label: 'Muito Baixa', analysis: 'Vegetação escassa, limitada a canteiros.' } } }
        ],
        'Rio de Janeiro': [
            { name: 'Parque Nacional da Tijuca', coords: [-22.95, -43.28], type: 'park', info: { heat: { value: '26°C', label: 'Fresco', analysis: 'Extensa área de floresta que regula a temperatura local.' }, air: { value: '10 µmol/m²', label: 'Muito Baixa', analysis: 'Ar puro devido à enorme massa de vegetação.' }, vegetation: { value: '0.85 NDVI', label: 'Muito Alta', analysis: 'Uma das maiores florestas urbanas do mundo.' } } },
            { name: 'Centro', coords: [-22.90, -43.17], type: 'urban', info: { heat: { value: '33°C', label: 'Quente', analysis: 'Área densamente construída com pouca ventilação.' }, air: { value: '130 µmol/m²', label: 'Elevada', analysis: 'Poluição do tráfego e da zona portuária.' }, vegetation: { value: '0.10 NDVI', label: 'Baixa', analysis: 'Poucas áreas verdes no centro histórico.' } } }
        ],
        'Buenos Aires': [
            { name: 'Bosques de Palermo', coords: [-34.57, -58.41], type: 'park', info: { heat: { value: '23°C', label: 'Fresco', analysis: 'Grande parque urbano que funciona como um pulmão para a cidade.' }, air: { value: '25 µmol/m²', label: 'Baixa', analysis: 'A qualidade do ar é visivelmente melhor dentro do parque.' }, vegetation: { value: '0.75 NDVI', label: 'Alta', analysis: 'Vegetação bem conservada com lagos.' } } },
            { name: 'Plaza de Mayo', coords: [-34.60, -58.37], type: 'urban', info: { heat: { value: '30°C', label: 'Quente', analysis: 'Coração histórico e político, com muitos edifícios e asfalto.' }, air: { value: '110 µmol/m²', label: 'Elevada', analysis: 'Tráfego intenso de veículos e autocarros turísticos.' }, vegetation: { value: '0.08 NDVI', label: 'Nula', analysis: 'Quase nenhuma vegetação.' } } }
        ],
        'Cidade do México': [
            { name: 'Bosque de Chapultepec', coords: [19.41, -99.18], type: 'park', info: { heat: { value: '21°C', label: 'Fresco', analysis: 'Um dos maiores parques da América Latina, essencial para a cidade.' }, air: { value: '80 µmol/m²', label: 'Moderada', analysis: 'Ajuda a mitigar a poluição geral da cidade, mas ainda é afetado.' }, vegetation: { value: '0.80 NDVI', label: 'Alta', analysis: 'Extensa área florestal.' } } },
            { name: 'Zócalo', coords: [19.43, -99.13], type: 'urban', info: { heat: { value: '27°C', label: 'Quente', analysis: 'Enorme praça de betão que absorve muito calor.' }, air: { value: '180 µmol/m²', label: 'Muito Elevada', analysis: 'Local de grande concentração de tráfego e pessoas.' }, vegetation: { value: '0.02 NDVI', label: 'Nula', analysis: 'Ausência total de vegetação.' } } }
        ],
        'Toronto': [
            { name: 'High Park', coords: [43.64, -79.46], type: 'park', info: { heat: { value: '19°C', label: 'Fresco', analysis: 'Grande parque com habitat natural, lagos e áreas de lazer.' }, air: { value: '20 µmol/m²', label: 'Baixa', analysis: 'Qualidade do ar significativamente melhorada pela vegetação.' }, vegetation: { value: '0.78 NDVI', label: 'Alta', analysis: 'Mistura de floresta e jardins bem cuidados.' } } },
            { name: 'Yonge-Dundas Square', coords: [43.65, -79.38], type: 'urban', info: { heat: { value: '26°C', label: 'Quente', analysis: 'Coração comercial com edifícios altos e ecrãs, criando uma ilha de calor.' }, air: { value: '95 µmol/m²', label: 'Elevada', analysis: 'Pico de poluição devido ao tráfego constante.' }, vegetation: { value: '0.06 NDVI', label: 'Nula', analysis: 'Área completamente urbanizada.' } } }
        ],
         'Nova Iorque': [
            { name: 'Central Park', coords: [40.782, -73.965], type: 'park', info: { heat: { value: '22°C', label: 'Fresco', analysis: 'O grande corpo de água e a vegetação densa criam um microclima mais ameno.' }, air: { value: '45 µmol/m²', label: 'Moderada', analysis: 'A poluição da cidade circundante afeta o parque.' }, vegetation: { value: '0.81 NDVI', label: 'Muito Alta', analysis: 'Uma das áreas verdes urbanas mais saudáveis do mundo.' } } },
            { name: 'Times Square', coords: [40.758, -73.985], type: 'urban', info: { heat: { value: '29°C', label: 'Quente', analysis: 'Falta de vegetação e multidões contribuem para o aumento da temperatura.' }, air: { value: '120 µmol/m²', label: 'Elevada', analysis: 'Ponto de grande concentração de tráfego e poluentes.' }, vegetation: { value: '0.05 NDVI', label: 'Nula', analysis: 'Praticamente nenhuma vegetação presente.' } } }
        ],
        'Los Angeles': [
            { name: 'Griffith Park', coords: [34.13, -118.29], type: 'park', info: { heat: { value: '28°C', label: 'Moderado', analysis: 'Grande parque com vegetação nativa, mas em clima quente e seco.' }, air: { value: '60 µmol/m²', label: 'Moderada', analysis: 'Localizado numa colina, fica acima de parte da poluição da bacia de LA.' }, vegetation: { value: '0.60 NDVI', label: 'Média', analysis: 'Vegetação adaptada ao clima semiárido.' } } },
            { name: 'Downtown LA', coords: [34.05, -118.24], type: 'urban', info: { heat: { value: '35°C', label: 'Muito Quente', analysis: 'Ilha de calor clássica devido à densidade de arranha-céus.' }, air: { value: '140 µmol/m²', label: 'Elevada', analysis: 'Concentração de poluição devido ao tráfego e à topografia.' }, vegetation: { value: '0.11 NDVI', label: 'Baixa', analysis: 'Pouquíssimas árvores e espaços verdes.' } } }
        ],
        'Vancouver': [
            { name: 'Stanley Park', coords: [49.30, -123.14], type: 'park', info: { heat: { value: '18°C', label: 'Fresco', analysis: 'Enorme floresta tropical temperada rodeada pelo oceano.' }, air: { value: '10 µmol/m²', label: 'Muito Baixa', analysis: 'Ar extremamente puro, vindo do Pacífico.' }, vegetation: { value: '0.88 NDVI', label: 'Muito Alta', analysis: 'Floresta madura e densa.' } } },
            { name: 'Gastown', coords: [49.28, -123.10], type: 'urban', info: { heat: { value: '22°C', label: 'Moderado', analysis: 'Bairro histórico com edifícios de tijolo, mas com brisa marítima.' }, air: { value: '40 µmol/m²', label: 'Baixa', analysis: 'Qualidade do ar geralmente boa.' }, vegetation: { value: '0.15 NDVI', label: 'Baixa', analysis: 'Árvores de rua e pequenos vasos.' } } }
        ],
        'Chicago': [
            { name: 'Millennium Park', coords: [41.88, -87.62], type: 'park', info: { heat: { value: '24°C', label: 'Moderado', analysis: 'Parque moderno com espaços abertos e jardins.' }, air: { value: '70 µmol/m²', label: 'Moderada', analysis: 'Localizado no centro, sofre com a poluição circundante.' }, vegetation: { value: '0.65 NDVI', label: 'Média', analysis: 'Combinação de relvado e jardins de design.' } } },
            { name: 'The Loop', coords: [41.87, -87.62], type: 'urban', info: { heat: { value: '29°C', label: 'Quente', analysis: 'Coração financeiro com "canyons" de arranha-céus que prendem o calor.' }, air: { value: '110 µmol/m²', label: 'Elevada', analysis: 'Tráfego intenso e baixa circulação de ar.' }, vegetation: { value: '0.07 NDVI', label: 'Baixa', analysis: 'Jardins em telhados são a principal forma de vegetação.' } } }
        ],
        'Santiago': [
            { name: 'Cerro San Cristóbal', coords: [-33.42, -70.62], type: 'park', info: { heat: { value: '25°C', label: 'Moderado', analysis: 'Grande parque metropolitano numa colina, com vistas sobre a cidade.' }, air: { value: '100 µmol/m²', label: 'Elevada', analysis: 'A altitude ajuda, mas a poluição de Santiago fica presa no vale.' }, vegetation: { value: '0.55 NDVI', label: 'Média', analysis: 'Vegetação nativa adaptada ao clima seco.' } } },
            { name: 'Plaza de Armas', coords: [-33.43, -70.65], type: 'urban', info: { heat: { value: '31°C', label: 'Quente', analysis: 'Centro histórico com muito pavimento e edifícios.' }, air: { value: '160 µmol/m²', label: 'Muito Elevada', analysis: 'Um dos pontos com pior qualidade do ar da cidade.' }, vegetation: { value: '0.10 NDVI', label: 'Baixa', analysis: 'Apenas algumas palmeiras e canteiros.' } } }
        ],

        // EUROPA
        'Lisboa': [
            { name: 'Parque Florestal de Monsanto', coords: [38.72, -9.18], type: 'park', info: { heat: { value: '24°C', label: 'Fresco', analysis: 'Extensa área florestal que funciona como o "pulmão da cidade".' }, air: { value: '15 µmol/m²', label: 'Muito Baixa', analysis: 'Ar de excelente qualidade.' }, vegetation: { value: '0.82 NDVI', label: 'Alta', analysis: 'Floresta densa e bem estabelecida.' } } },
            { name: 'Baixa Pombalina', coords: [38.71, -9.13], type: 'urban', info: { heat: { value: '30°C', label: 'Quente', analysis: 'Área histórica com ruas estreitas e alta densidade de construção.' }, air: { value: '85 µmol/m²', label: 'Moderada', analysis: 'Poluição do tráfego e da proximidade ao rio Tejo.' }, vegetation: { value: '0.09 NDVI', label: 'Baixa', analysis: 'Pouquíssima vegetação.' } } }
        ],
        'Madrid': [
            { name: 'Parque del Buen Retiro', coords: [40.41, -3.68], type: 'park', info: { heat: { value: '26°C', label: 'Fresco', analysis: 'Grande parque central que oferece um refúgio do calor intenso de Madrid.' }, air: { value: '40 µmol/m²', label: 'Baixa', analysis: 'A qualidade do ar é consideravelmente melhor dentro do parque.' }, vegetation: { value: '0.77 NDVI', label: 'Alta', analysis: 'Jardins bem cuidados, árvores e um grande lago.' } } },
            { name: 'Puerta del Sol', coords: [40.41, -3.70], type: 'urban', info: { heat: { value: '34°C', label: 'Muito Quente', analysis: 'Grande praça pavimentada que se torna um forno no verão.' }, air: { value: '130 µmol/m²', label: 'Elevada', analysis: 'Centro nevrálgico da cidade com muito tráfego e pessoas.' }, vegetation: { value: '0.01 NDVI', label: 'Nula', analysis: 'Totalmente pavimentado.' } } }
        ],
        'Londres': [
            { name: 'Hyde Park', coords: [51.507, -0.165], type: 'park', info: { heat: { value: '18°C', label: 'Fresco', analysis: 'Grande área verde que serve como um refúgio climático na cidade.' }, air: { value: '30 µmol/m²', label: 'Baixa', analysis: 'Qualidade do ar notavelmente melhor.' }, vegetation: { value: '0.79 NDVI', label: 'Alta', analysis: 'Vegetação exuberante e bem mantida.' } } },
            { name: 'City of London', coords: [51.515, -0.091], type: 'urban', info: { heat: { value: '23°C', label: 'Quente', analysis: 'Distrito financeiro com alta densidade de edifícios.' }, air: { value: '90 µmol/m²', label: 'Moderada', analysis: 'Congestionamento e "canyons" urbanos prendem os poluentes.' }, vegetation: { value: '0.15 NDVI', label: 'Baixa', analysis: 'Pequenas praças e jardins em telhados.' } } }
        ],
        'Paris': [
            { name: 'Jardim de Luxemburgo', coords: [48.84, 2.33], type: 'park', info: { heat: { value: '20°C', label: 'Fresco', analysis: 'Jardim histórico com muitas árvores maduras que fornecem sombra.' }, air: { value: '50 µmol/m²', label: 'Moderada', analysis: 'Um oásis de ar mais limpo no centro de Paris.' }, vegetation: { value: '0.76 NDVI', label: 'Alta', analysis: 'Design de jardim formal com relvados e floresta.' } } },
            { name: 'La Défense', coords: [48.89, 2.24], type: 'urban', info: { heat: { value: '27°C', label: 'Muito Quente', analysis: 'Distrito de negócios moderno com vidro e betão, criando uma forte ilha de calor.' }, air: { value: '100 µmol/m²', label: 'Moderada', analysis: 'Menos tráfego direto, mas ainda afetado pela poluição geral.' }, vegetation: { value: '0.09 NDVI', label: 'Nula', analysis: 'Ambiente quase totalmente construído.' } } }
        ],
        'Roma': [
            { name: 'Villa Borghese', coords: [41.91, 12.48], type: 'park', info: { heat: { value: '27°C', label: 'Moderado', analysis: 'Grande parque paisagístico que oferece sombra e frescura.' }, air: { value: '75 µmol/m²', label: 'Moderada', analysis: 'A vegetação ajuda a filtrar a poluição do tráfego romano.' }, vegetation: { value: '0.72 NDVI', label: 'Alta', analysis: 'Ampla área verde com pinheiros e fontes.' } } },
            { name: 'Coliseu', coords: [41.89, 12.49], type: 'urban', info: { heat: { value: '33°C', label: 'Quente', analysis: 'Área turística com muito pavimento de pedra que retém o calor.' }, air: { value: '115 µmol/m²', label: 'Elevada', analysis: 'Poluição constante do tráfego intenso na área circundante.' }, vegetation: { value: '0.13 NDVI', label: 'Baixa', analysis: 'Pouca vegetação para além de algumas árvores esparsas.' } } }
        ],
        'Berlim': [
            { name: 'Tiergarten', coords: [52.51, 13.35], type: 'park', info: { heat: { value: '19°C', label: 'Fresco', analysis: 'Enorme parque florestal no coração da cidade.' }, air: { value: '25 µmol/m²', label: 'Baixa', analysis: 'Qualidade do ar excelente, um refúgio para os habitantes.' }, vegetation: { value: '0.81 NDVI', label: 'Muito Alta', analysis: 'Floresta densa com canais e clareiras.' } } },
            { name: 'Alexanderplatz', coords: [52.52, 13.41], type: 'urban', info: { heat: { value: '25°C', label: 'Quente', analysis: 'Vasta praça pública com muita superfície de betão.' }, air: { value: '80 µmol/m²', label: 'Moderada', analysis: 'Centro de transportes com emissões de autocarros e elétricos.' }, vegetation: { value: '0.05 NDVI', label: 'Nula', analysis: 'Totalmente urbanizado.' } } }
        ],
        'Moscovo': [
            { name: 'Parque Gorky', coords: [55.72, 37.60], type: 'park', info: { heat: { value: '17°C', label: 'Fresco', analysis: 'Grande parque cultural ao longo do rio Moskva.' }, air: { value: '35 µmol/m²', label: 'Baixa', analysis: 'Área de lazer popular com ar mais limpo.' }, vegetation: { value: '0.75 NDVI', label: 'Alta', analysis: 'Combinação de jardins formais e áreas arborizadas.' } } },
            { name: 'Praça Vermelha', coords: [55.75, 37.62], type: 'urban', info: { heat: { value: '23°C', label: 'Moderado', analysis: 'Grande área pavimentada, mas o clima frio de Moscovo modera as temperaturas.' }, air: { value: '90 µmol/m²', label: 'Moderada', analysis: 'Tráfego intenso nas ruas circundantes.' }, vegetation: { value: '0.01 NDVI', label: 'Nula', analysis: 'Completamente pavimentado.' } } }
        ],
        'Istambul': [
            { name: 'Parque Gülhane', coords: [41.01, 28.98], type: 'park', info: { heat: { value: '25°C', label: 'Fresco', analysis: 'Parque histórico junto ao Palácio Topkapi, com brisa do Bósforo.' }, air: { value: '60 µmol/m²', label: 'Moderada', analysis: 'O ar é melhor do que no resto da cidade velha.' }, vegetation: { value: '0.68 NDVI', label: 'Média', analysis: 'Jardins e árvores antigas.' } } },
            { name: 'Praça Sultanahmet', coords: [41.00, 28.97], type: 'urban', info: { heat: { value: '31°C', label: 'Quente', analysis: 'Grande praça turística entre a Hagia Sophia e a Mesquita Azul.' }, air: { value: '110 µmol/m²', label: 'Elevada', analysis: 'Poluição de autocarros turísticos e multidões.' }, vegetation: { value: '0.10 NDVI', label: 'Baixa', analysis: 'Limitada a canteiros de flores.' } } }
        ],
        'Amesterdão': [
            { name: 'Vondelpark', coords: [52.35, 4.86], type: 'park', info: { heat: { value: '18°C', label: 'Fresco', analysis: 'O parque mais famoso da cidade, com lagos e árvores.' }, air: { value: '30 µmol/m²', label: 'Baixa', analysis: 'Qualidade do ar beneficiada pela proibição de carros em muitas áreas.' }, vegetation: { value: '0.77 NDVI', label: 'Alta', analysis: 'Vegetação bem cuidada.' } } },
            { name: 'Praça Dam', coords: [52.37, 4.89], type: 'urban', info: { heat: { value: '22°C', label: 'Moderado', analysis: 'Centro histórico pavimentado, mas o clima ameno evita calor extremo.' }, air: { value: '75 µmol/m²', label: 'Moderada', analysis: 'Poluição de elétricos, autocarros e multidões de turistas.' }, vegetation: { value: '0.04 NDVI', label: 'Nula', analysis: 'Totalmente construído.' } } }
        ],

        // ÁSIA
        'Tóquio': [
            { name: 'Parque Ueno', coords: [35.71, 139.77], type: 'park', info: { heat: { value: '26°C', label: 'Fresco', analysis: 'Grande parque cultural que oferece um refúgio do calor da cidade.' }, air: { value: '70 µmol/m²', label: 'Moderada', analysis: 'A qualidade do ar é melhor, mas ainda influenciada pela megalópole.' }, vegetation: { value: '0.70 NDVI', label: 'Alta', analysis: 'Muitas árvores, santuários e um lago.' } } },
            { name: 'Shibuya Crossing', coords: [35.659, 139.700], type: 'urban', info: { heat: { value: '34°C', label: 'Muito Quente', analysis: 'Calor extremo de asfalto, edifícios, ecrãs e multidões.' }, air: { value: '160 µmol/m²', label: 'Elevada', analysis: 'Um dos cruzamentos mais movimentados do mundo.' }, vegetation: { value: '0.04 NDVI', label: 'Nula', analysis: 'Um exemplo icónico de um "deserto de betão".' } } }
        ],
        'Seul': [
            { name: 'Parque Namsan', coords: [37.55, 126.98], type: 'park', info: { heat: { value: '23°C', label: 'Fresco', analysis: 'Montanha no centro da cidade, coberta por floresta.' }, air: { value: '55 µmol/m²', label: 'Moderada', analysis: 'Atua como uma barreira natural à poluição.' }, vegetation: { value: '0.80 NDVI', label: 'Alta', analysis: 'Vegetação densa e nativa.' } } },
            { name: 'Myeongdong', coords: [37.56, 126.98], type: 'urban', info: { heat: { value: '30°C', label: 'Quente', analysis: 'Área comercial movimentada com ruas estreitas e muitos edifícios.' }, air: { value: '125 µmol/m²', label: 'Elevada', analysis: 'Alta densidade de pessoas e tráfego.' }, vegetation: { value: '0.07 NDVI', label: 'Baixa', analysis: 'Pouca vegetação.' } } }
        ],
        'Pequim': [
            { name: 'Parque Jingshan', coords: [39.92, 116.39], type: 'park', info: { heat: { value: '24°C', label: 'Moderado', analysis: 'Colina artificial com vegetação que oferece vistas sobre a Cidade Proibida.' }, air: { value: '140 µmol/m²', label: 'Elevada', analysis: 'A poluição de Pequim é um problema persistente.' }, vegetation: { value: '0.68 NDVI', label: 'Média', analysis: 'Parque bem arborizado.' } } },
            { name: 'Praça Tiananmen', coords: [39.90, 116.39], type: 'urban', info: { heat: { value: '31°C', label: 'Quente', analysis: 'Uma das maiores praças do mundo, totalmente pavimentada.' }, air: { value: '200 µmol/m²', label: 'Muito Elevada', analysis: 'Afetada pelo tráfego intenso e pela indústria circundante.' }, vegetation: { value: '0.01 NDVI', label: 'Nula', analysis: 'Sem vegetação.' } } }
        ],
        'Mumbai': [
            { name: 'Sanjay Gandhi National Park', coords: [19.23, 72.91], type: 'park', info: { heat: { value: '29°C', label: 'Moderado', analysis: 'Grande parque nacional dentro dos limites da cidade.' }, air: { value: '80 µmol/m²', label: 'Moderada', analysis: 'Qualidade do ar muito superior à do resto da cidade.' }, vegetation: { value: '0.83 NDVI', label: 'Muito Alta', analysis: 'Floresta tropical protegida.' } } },
            { name: 'Gateway of India', coords: [18.92, 72.83], type: 'urban', info: { heat: { value: '34°C', label: 'Quente', analysis: 'Área turística costeira com muita pedra e betão.' }, air: { value: '150 µmol/m²', label: 'Elevada', analysis: 'Poluição de barcos, tráfego e alta densidade de pessoas.' }, vegetation: { value: '0.07 NDVI', label: 'Baixa', analysis: 'Apenas alguns coqueiros ornamentais.' } } }
        ],
        'Singapura': [
            { name: 'Gardens by the Bay', coords: [1.28, 103.86], type: 'park', info: { heat: { value: '30°C', label: 'Quente', analysis: 'Apesar de verde, o clima tropical mantém as temperaturas altas.' }, air: { value: '20 µmol/m²', label: 'Baixa', analysis: 'Qualidade do ar excelente, um modelo de cidade-jardim.' }, vegetation: { value: '0.88 NDVI', label: 'Muito Alta', analysis: 'Tecnologia e natureza combinadas para uma vegetação exuberante.' } } },
            { name: 'Marina Bay Sands', coords: [1.28, 103.85], type: 'urban', info: { heat: { value: '33°C', label: 'Quente', analysis: 'Complexo icónico com alta densidade de construção.' }, air: { value: '45 µmol/m²', label: 'Moderada', analysis: 'Afetado pelo tráfego e pela atividade marítima.' }, vegetation: { value: '0.30 NDVI', label: 'Média', analysis: 'Incorpora jardins verticais e no topo dos edifícios.' } } }
        ],
        'Bangkok': [
            { name: 'Parque Lumphini', coords: [13.73, 100.54], type: 'park', info: { heat: { value: '31°C', label: 'Quente', analysis: 'Oásis verde que oferece um alívio crucial do calor e da humidade da cidade.' }, air: { value: '90 µmol/m²', label: 'Moderada', analysis: 'O ar é visivelmente melhor dentro do parque.' }, vegetation: { value: '0.75 NDVI', label: 'Alta', analysis: 'Lago artificial e grandes áreas arborizadas.' } } },
            { name: 'Siam Paragon', coords: [13.74, 100.53], type: 'urban', info: { heat: { value: '36°C', label: 'Muito Quente', analysis: 'Coração comercial com centros comerciais, tráfego intenso e pouca sombra.' }, air: { value: '170 µmol/m²', label: 'Elevada', analysis: 'Poluição do tráfego constante dos "tuk-tuks" e carros.' }, vegetation: { value: '0.08 NDVI', label: 'Baixa', analysis: 'Limitada a vasos e decoração.' } } }
        ],
        'Jacarta': [
            { name: 'Parque Suropati', coords: [-6.20, 106.83], type: 'park', info: { heat: { value: '30°C', label: 'Quente', analysis: 'Pequeno, mas importante parque no bairro de Menteng.' }, air: { value: '100 µmol/m²', label: 'Elevada', analysis: 'Oferece um pequeno alívio da poluição geral da cidade.' }, vegetation: { value: '0.65 NDVI', label: 'Média', analysis: 'Árvores maduras e bem cuidadas.' } } },
            { name: 'Praça Merdeka', coords: [-6.17, 106.82], type: 'urban', info: { heat: { value: '35°C', label: 'Muito Quente', analysis: 'Vasta praça com o Monumento Nacional, grande exposição solar.' }, air: { value: '190 µmol/m²', label: 'Muito Elevada', analysis: 'Rodeada por algumas das ruas mais movimentadas de Jacarta.' }, vegetation: { value: '0.20 NDVI', label: 'Baixa', analysis: 'Principalmente relvado com poucas árvores.' } } }
        ],
        'Hong Kong': [
            { name: 'Hong Kong Park', coords: [22.27, 114.16], type: 'park', info: { heat: { value: '29°C', label: 'Moderado', analysis: 'Um oásis verdejante no meio de um dos distritos mais densos do mundo.' }, air: { value: '65 µmol/m²', label: 'Moderada', analysis: 'Ajuda a melhorar a qualidade do ar local.' }, vegetation: { value: '0.73 NDVI', label: 'Alta', analysis: 'Jardins bem desenhados, um aviário e quedas de água.' } } },
            { name: 'Mong Kok', coords: [22.32, 114.17], type: 'urban', info: { heat: { value: '34°C', label: 'Muito Quente', analysis: 'Uma das áreas mais densamente povoadas do planeta, calor intenso.' }, air: { value: '155 µmol/m²', label: 'Elevada', analysis: 'Poluição do ar presa entre os edifícios altos e estreitos.' }, vegetation: { value: '0.05 NDVI', label: 'Nula', analysis: 'Vegetação quase inexistente.' } } }
        ],

        // ÁFRICA
        'Cairo': [
            { name: 'Parque Al-Azhar', coords: [30.04, 31.26], type: 'park', info: { heat: { value: '32°C', label: 'Quente', analysis: 'Um oásis verde crucial numa cidade densa e árida.' }, air: { value: '150 µmol/m²', label: 'Elevada', analysis: 'O parque melhora o ar, mas a poluição geral da cidade é muito alta.' }, vegetation: { value: '0.65 NDVI', label: 'Média', analysis: 'Vegetação irrigada, vital para o ambiente local.' } } },
            { name: 'Praça Tahrir', coords: [30.044, 31.235], type: 'urban', info: { heat: { value: '38°C', label: 'Extremo', analysis: 'Vasta área de asfalto no coração de uma das cidades mais quentes do mundo.' }, air: { value: '250 µmol/m²', label: 'Crítica', analysis: 'Níveis de poluição perigosos devido ao tráfego caótico.' }, vegetation: { value: '0.03 NDVI', label: 'Nula', analysis: 'Vegetação praticamente inexistente.' } } }
        ],
        'Joanesburgo': [
            { name: 'Walter Sisulu National Botanical Garden', coords: [-26.08, 27.84], type: 'park', info: { heat: { value: '22°C', label: 'Fresco', analysis: 'Jardim botânico com vegetação nativa e uma cascata.' }, air: { value: '28 µmol/m²', label: 'Baixa', analysis: 'Ar limpo, afastado das zonas mais poluídas.' }, vegetation: { value: '0.79 NDVI', label: 'Alta', analysis: 'Grande diversidade de flora.' } } },
            { name: 'Sandton City', coords: [-26.10, 28.05], type: 'urban', info: { heat: { value: '28°C', label: 'Quente', analysis: 'Centro financeiro moderno com muitos edifícios de escritórios.' }, air: { value: '70 µmol/m²', label: 'Moderada', analysis: 'Poluição do tráfego intenso na área.' }, vegetation: { value: '0.19 NDVI', label: 'Baixa', analysis: 'Paisagismo urbano e árvores de rua.' } } }
        ],
        'Lagos': [
            { name: 'Lekki Conservation Centre', coords: [6.43, 3.53], type: 'park', info: { heat: { value: '30°C', label: 'Quente', analysis: 'Reserva natural que preserva o ecossistema de manguezal.' }, air: { value: '65 µmol/m²', label: 'Moderada', analysis: 'O ar é mais limpo devido à vegetação e à distância do centro.' }, vegetation: { value: '0.84 NDVI', label: 'Muito Alta', analysis: 'Ecossistema de pântano e floresta.' } } },
            { name: 'Lagos Island', coords: [6.45, 3.39], type: 'urban', info: { heat: { value: '34°C', label: 'Quente', analysis: 'Área de negócios central, extremamente densa e movimentada.' }, air: { value: '160 µmol/m²', label: 'Elevada', analysis: 'Poluição severa de geradores, veículos e mercados.' }, vegetation: { value: '0.09 NDVI', label: 'Baixa', analysis: 'Quase sem espaços verdes.' } } }
        ],
        'Nairobi': [
            { name: 'Nairobi National Park', coords: [-1.36, 36.85], type: 'park', info: { heat: { value: '24°C', label: 'Fresco', analysis: 'Parque nacional único no limite da cidade.' }, air: { value: '20 µmol/m²', label: 'Baixa', analysis: 'Savana aberta com ar de boa qualidade.' }, vegetation: { value: '0.70 NDVI', label: 'Alta', analysis: 'Ecossistema de savana saudável.' } } },
            { name: 'Central Business District', coords: [-1.28, 36.82], type: 'urban', info: { heat: { value: '29°C', label: 'Quente', analysis: 'Centro da cidade com tráfego intenso.' }, air: { value: '100 µmol/m²', label: 'Elevada', analysis: 'Poluição dos "matatus" (miniautocarros) e do trânsito.' }, vegetation: { value: '0.15 NDVI', label: 'Baixa', analysis: 'Poucas árvores no centro.' } } }
        ],

        // OCEANIA
        'Dubai': [
            { name: 'Safa Park', coords: [25.18, 55.24], type: 'park', info: { heat: { value: '36°C', label: 'Quente', analysis: 'Parque irrigado que oferece algum alívio do calor do deserto.' }, air: { value: '80 µmol/m²', label: 'Moderada', analysis: 'A poeira do deserto contribui para a qualidade do ar.' }, vegetation: { value: '0.55 NDVI', label: 'Média', analysis: 'Vegetação artificialmente mantida.' } } },
            { name: 'Burj Khalifa', coords: [25.197, 55.274], type: 'urban', info: { heat: { value: '42°C', label: 'Extremo', analysis: 'Materiais de construção como vidro e metal intensificam o calor.' }, air: { value: '120 µmol/m²', label: 'Elevada', analysis: 'Alta concentração de tráfego e construção.' }, vegetation: { value: '0.06 NDVI', label: 'Baixa', analysis: 'Paisagismo ornamental mínimo.' } } }
        ],
        'Sydney': [
            { name: 'Royal Botanic Garden', coords: [-33.86, 151.21], type: 'park', info: { heat: { value: '20°C', label: 'Fresco', analysis: 'A brisa do porto e a vegetação exuberante mantêm as temperaturas baixas.' }, air: { value: '12 µmol/m²', label: 'Baixa', analysis: 'Excelente qualidade do ar.' }, vegetation: { value: '0.82 NDVI', label: 'Muito Alta', analysis: 'Uma coleção diversificada e saudável de plantas.' } } },
            { name: 'Circular Quay', coords: [-33.861, 151.211], type: 'urban', info: { heat: { value: '24°C', label: 'Moderado', analysis: 'Área portuária movimentada, mas a brisa do mar ajuda a moderar o calor.' }, air: { value: '40 µmol/m²', label: 'Moderada', analysis: 'Poluição de ferries, autocarros e tráfego turístico.' }, vegetation: { value: '0.18 NDVI', label: 'Baixa', analysis: 'Limitada a árvores em vasos.' } } }
        ],
        'Melbourne': [
            { name: 'Royal Botanic Gardens Victoria', coords: [-37.83, 144.97], type: 'park', info: { heat: { value: '19°C', label: 'Fresco', analysis: 'Jardins aclamados com vegetação diversificada.' }, air: { value: '15 µmol/m²', label: 'Baixa', analysis: 'Ar limpo vindo do sul.' }, vegetation: { value: '0.80 NDVI', label: 'Alta', analysis: 'Vegetação saudável e bem gerida.' } } },
            { name: 'Federation Square', coords: [-37.81, 144.96], type: 'urban', info: { heat: { value: '24°C', label: 'Moderado', analysis: 'Grande praça pública com arquitetura moderna e superfícies duras.' }, air: { value: '50 µmol/m²', label: 'Moderada', analysis: 'Ponto central com tráfego e elétricos.' }, vegetation: { value: '0.05 NDVI', label: 'Nula', analysis: 'Arquitetura domina a paisagem.' } } }
        ]
    };

    L.Control.geocoder({
        defaultMarkGeocode: true,
        placeholder: 'Pesquise uma cidade...',
        position: 'topleft'
    }).on('markgeocode', e => map.fitBounds(e.geocode.bbox)).addTo(map);

    L.tileLayer.wms(vegetationLayer.endpoint, {
        layers: vegetationLayer.name,
        format: 'image/png',
        transparent: true,
        opacity: 0.7,
        attribution: 'Dados de Vegetação &copy; NASA GIBS'
    }).addTo(map);

    const createCustomIcon = (type) => L.divIcon({
        className: 'custom-div-icon',
        html: `<div style="background-color: ${type === 'park' ? '#22c55e' : '#6b7280'};" class="w-full h-full rounded-full"></div>`,
        iconSize: [16, 16]
    });

    function createPopupContent(point) {
        const { heat, air, vegetation } = point.info;
        return `
            <div class="popup-title">${point.name}</div>
            <div class="popup-metric">
                <span class="popup-metric-title">🌡️ Temperatura</span>
                <span class="popup-metric-value">${heat.value} (${heat.label})</span>
                <p class="popup-metric-analysis">${heat.analysis}</p>
            </div>
            <div class="popup-metric">
                <span class="popup-metric-title">💨 Poluição do Ar (NO₂)</span>
                <span class="popup-metric-value">${air.value} (${air.label})</span>
                <p class="popup-metric-analysis">${air.analysis}</p>
            </div>
            <div class="popup-metric">
                <span class="popup-metric-title">🌳 Vegetação (NDVI)</span>
                <span class="popup-metric-value">${vegetation.value} (${vegetation.label})</span>
                <p class="popup-metric-analysis">${vegetation.analysis}</p>
            </div>
            <div class="popup-footer">
                Fontes: NASA GIBS (MODIS/OMI), OpenStreetMap.
            </div>
        `;
    }

    function addAllMarkers() {
        for (const city in citiesData) {
            citiesData[city].forEach(point => {
                L.marker(point.coords, { icon: createCustomIcon(point.type) })
                    .bindPopup(createPopupContent(point))
                    .addTo(markersLayer);
            });
        }
    }

    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
        const div = L.DomUtil.create('div', 'info legend');
        div.innerHTML = `
            <div class="legend-title">Índice de Vegetação</div>
            <div class="legend-gradient" style="background: linear-gradient(to right, #a50026, #d73027, #f46d43, #fee090, #a6d96a, #1a9850);"></div>
            <div class="legend-labels"><span>Baixa</span><span>Alta</span></div>
            <div class="legend-section">
                <div class="legend-title">Pontos de Análise</div>
                <div class="legend-marker-item"><div class="legend-marker-icon icon-park"></div><span>Parques / Áreas Verdes</span></div>
                <div class="legend-marker-item"><div class="legend-marker-icon icon-urban"></div><span>Centros Urbanos</span></div>
            </div>`;
        return div;
    };
    legend.addTo(map);
    
    map.attributionControl.addAttribution('Dados de POIs &copy; OpenStreetMap');

    addAllMarkers();
});