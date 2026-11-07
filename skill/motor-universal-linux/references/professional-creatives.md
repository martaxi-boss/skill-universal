# Padrão profissional de criativos publicitários — Ferrari

Data: 07/11/2026. Aplica-se na Skill universal, sem criar um segundo motor, catálogo ou serviço. A qualidade final depende de avaliação humana.

## Preferência de voz confirmada pelo proprietário

O utilizador enviou 1000183150.mp4 (44,8 s) em 07/11/2026 como exemplo de voz que **aprova**. A locução do projeto martaxi-boss/Criativos-anuncios, feita com Piper pt_PT-tugão-medium, passa a ser a primeira escolha. Não propor substituir essa voz por outra para o mesmo anúncio sem solicitação; gravar uma nova locução para cada guião e testar o áudio resultante.

O proprietário também rejeitou a necessidade de fornecer fotografias manualmente. Um URL de site deve acionar primeiro o fluxo de captura pública descrito em automatic-creative-from-url.md. O código GitHub pode diferir da produção: a captura verdadeira da página é a fonte visual primária. Reels têm limites diferentes de acessibilidade.

## Fonte de marca obrigatória

Usar, pela ordem: (1) domínio real atual, capturas confirmadas com data; (2) repositório de código, com etiqueta «apenas fonte GitHub, produção não verificada»; (3) materiais autorizados do proprietário. Capturas antigas, templates inventados, logótipos reconstruídos e fotografias de demonstração não substituem visuais reais. Os preços exigem data/fonte e devem ser apresentados como observados, não garantidos.

### Exemplo Lowcost Europa — referência no código GitHub

Fonte: martaxi-boss/lowcost-europa, apps/storefront/templates/storefront/home.html e base.html e apps/storefront/static/storefront/storefront.css (07/11/2026). Não equivale a confirmação do deploy.

- Fundo #f7f7f2; verde de marca #164f42; verde escuro #103c32; texto #182923; superfícies #ffffff e #edf3ef.
- Fonte: Inter/sistema; logótipo original: storefront/lowcost-europa-brand-main.webp.
- Mensagem da página: «Tecnologia para a estética. Escolhas com critério.»; CTA principal: «VER EQUIPAMENTOS E PREÇOS».
- Mostrar produtos de estética profissional e fotos verdadeiras, a pesquisa, as categorias reais, preços observados, condições do parceiro e opções de envio apenas quando confirmadas.
- O vídeo lowcost_europa_anuncio_20s_ptpt.mp4 recebido tem cartões predominantemente azul-marinho/roxo, mockups genéricos e repete a cena «Explore por especialidade» em quadros seguidos. Foi rejeitado; não é modelo de qualidade aprovado.

## Storyboard de referência — 20 s, 9:16, português de Portugal

Texto para locução de teste, não áudio já aprovado:
«Procuras equipamentos de estética profissional? Na Lowcost Europa encontras categorias organizadas e preços observados. Compara as opções, verifica o envio para Portugal e escolhe com mais informação. Lowcost Europa: escolhas com critério.»

Sequência recomendada:
1. 0–2 s: equipamento verdadeiro num plano de destaque; gancho claro.
2. 2–6 s: dois/três equipamentos de categorias reais com enquadramento dinâmico.
3. 6–11 s: pesquisa e seleção reais do site, sem inventar uma interface.
4. 11–16 s: detalhe factual de produto, preço observado e parceiro quando houver prova.
5. 16–20 s: logótipo original, CTA «VER EQUIPAMENTOS E PREÇOS» e domínio confirmado.

Exigir pelo menos 4 cenas visualmente distintas, produto visível, legenda sem som, margens seguras para Meta/Reels e evitar texto longo, animação artificial e segundos finais só com logótipo.

## Porta de voz natural ou realmente humana

**Voz literalmente humana:** locutor autorizado e gravação WAV limpa em pt-PT, com direitos de publicidade.

**TTS com qualidade potencialmente humana:** fazer um teste A/B com o MESMO texto e sem alterar a velocidade artificialmente. Piper pt_PT-tugão-medium existe no projeto independente martaxi-boss/Criativos-anuncios, mas naturalidade não está certificada pelo facto de renderizar. O projeto tts_eu_pt (Kokoro-82M adaptado ao pt-PT, licença Apache-2.0, CPU e pesos de ~313 MB; github.com/logus2k/tts_eu_pt) é uma alternativa CANDIDATA, nunca presumir instalada ou superior sem teste auditivo, de licença e de desempenho. Instalar no Ferrari apenas em pasta privada e após testes reais; nunca usar recursos, venv, modelos ou serviços de outro projeto.

Escutar e verificar pt-PT (não pt-BR), pontuação, pausas, acentuação, emoção, dicção dos nomes de produtos e da marca; rejeitar voz monótona, metálica, esganiçada ou acelerada. Sem amostra aprovada, não chamar a voz «humana» nem entregar anúncio final com locução robótica. Se ambas forem rejeitadas, parar e solicitar voz gravada autorizada; não fazer fallback para eSpeak.

Som: locução com volume confortável, música licenciada 12–18 dB abaixo da fala durante a narração, faixas separadas, sem clipping, sem cortes de palavras. ffprobe, loudness e verificação técnica NÃO provam naturalidade.

## Direção de arte — porta visual antes da etiqueta profissional

A lição dos criativos Low Cost Europa é que uma captura genuína do site pode ser **inadequada como fotografia publicitária**. Não capturar o artigo/cartão completo, com botões, preços, etiquetas, textos e margens, para o colar dentro de outro cartão no vídeo. Usar a fotografia real do produto ou um clip publicitário original. Se o próprio ficheiro de imagem inclui cartazes, textos e etiquetas impressos, a fotografia continua visualmente poluída; recortar apenas quando possível **sem falsificar ou eliminar características do equipamento** e procurar alternativas autênticas no mesmo site.

O ChatGPT anfitrião é responsável pela avaliação editorial: abrir `preview_scenes.jpg`, três imagens PNG em tamanho integral e o MP4/WAV; verificar equilíbrio, exposição, recorte, alinhamento, peso do texto, ritmo, identidades, foco visual, margens e legibilidade em telemóvel. Se detetar elementos duplicados ou produtos demasiado pequenos, rejeitar a versão, corrigir o layout e voltar a testar. Nenhum `technical_pass` significa `approved_for_ads`. Não pedir ao utilizador que faça manualmente as fotografias quando existirem materiais públicos adequados.

Para a voz já aprovada, preservar Piper pt_PT-tugão-medium, usar texto curto e `length_scale` cerca de 1.15–1.20, com pausas. Abrandar não significa aplicar `atempo<1` no áudio pronto, nem substituir a voz. Se o resultado não couber em 20s, reescrever o texto ou rever duração de forma transparente; nunca acelerar a fala.

## Publicidade primeiro: argumento original, depois imagens sincronizadas

A responsabilidade do criativo é da IA anfitriã do Ferrari, não do utilizador. Não pedir frases, fotografias, storyboard ou estilo de montagem se a fonte pública e o vídeo de voz aprovado estiverem disponíveis. Analisar a natureza e funcionamento do negócio e escrever um texto **explicativo e comercialmente útil**, em linguagem pt-PT; apoiar cada afirmação em fonte real. O papel da IA é organizar uma narrativa própria (gancho → como funciona/o que oferece → provas observáveis → CTA), não repetir simplesmente o H1 e cinco nomes de produtos.

Criar `business_brief.json`, definir `voice_sentences` próprias, selecionar imagens/planos correspondentes e conferir em `storyboard.json` que **cada frase é ilustrada pelo produto, serviço ou funcionalidade exata**. A sincronização usa os tempos reais da narração (Piper aprovado com pausa natural). O ritmo, número de cenas e detalhe visual dependem da duração e da história; nunca forçar três fotos nem distribuir cenas em tempos iguais sem sentido. `auto_script` serve de primeira prévia factual; um anúncio editorialmente profissional requer análise e escrita pelo agente anfitrião, revisão visual e escuta.

## Checklist de entrega

- [ ] brand_source_verified: URL/captura da produção ou indicação repository_only, sem alegar produção verificada.
- [ ] licensed_product_media: fotografias/ícones autorizados e produtos reais identificados.
- [ ] brand_consistency: cor, tipografia, logo, CTA e cenas sem repetição, aprovação visual.
- [ ] narration_origin: human_recording OU synthetic_pt_pt; nunca confundir.
- [ ] audition_approved_by_owner: teste auditivo real em pt-PT; sem aprovação é editorial_pending.
- [ ] technical_pass: MP4, WAV, duração, codec, áudio, frames e hashes de ficheiros.
- [ ] approved_for_ads: somente com critérios anteriores, licença e confirmação do proprietário; caso contrário preview_only.

**Limite do motor:** o catálogo único Ferrari inclui um programa candidato Piper, mas no estado documental de 07/11/2026 não dispõe de ação TTS integrada e certificada. Não anunciar uma locução do Ferrari sem prova de um pedido real, run ID e report.json. O projeto Criativos-anuncios fornece métodos e código reutilizáveis, sem dependências cruzadas com a VPS. Caso faltem recursos ou aprovação, entregar prévia e explicar o bloqueio em vez de fabricar sucesso.
