# Ferrari — criativos automáticos a partir do site, página ou Reel

Este guia pertence à mesma Skill universal. Usa métodos do projeto independente Criativos-anuncios, mas não instala dependências cruzadas na VPS Ferrari.

## Voz que já está aprovada

O vídeo 1000183150.mp4 (44,8 s; recebido 07/11/2026) mostra o timbre e ritmo de locução que o dono aprovou. O projeto martaxi-boss/Criativos-anuncios utiliza Piper pt_PT-tugão-medium, com modelo verificado por SHA-256, geração de WAV frase a frase e mistura em FFmpeg. **Preferir essa mesma voz**, sem procurar outro TTS nem exigir nova autorização para experimentar o estilo. Não declarar que é uma gravação humana; é síntese pt-PT. A nova locução e sincronismo exigem audição antes de aprovação comercial.

## Evidência real de referência — Low Cost Europa

Em 07/11/2026, a execução [#42335182728](https://github.com/martaxi-boss/Criativos-anuncios/actions/runs/42335182728) concluiu **SUCCESS** com URL único `https://lowcost-europa.duckdns.org/`, cinco cenas, três cartões de produtos retirados do DOM público, logótipo real, CTA real e narração sintetizada com o mesmo Piper pt_PT-tugão-medium do projeto. O MP4 durou **19,656 s**, 864 × 1536, H.264/AAC; `site_capture.json.editorial.mode=authentic_editorial_composition` e `report.json.approval_state=preview_only`. Os materiais foram captados sem fotografias fornecidas manualmente. O teste demonstra funcionamento técnico e autenticidade dos elementos, **não** aprovação artística ou direitos comerciais definitivos.

A montagem é uma recomposição publicitária de capturas de elementos visuais reais, não uma gravação literal do site. O código `editorial_scene.py` usa apenas imagens do cartão, logótipo e botão efetivamente captados na página. Quando esses elementos não existem, a fallback `editorial.mode=site_screenshots` conserva capturas reais e documenta o motivo. Proibir produtos, preços, logótipos e descontos fictícios.

## Regra fotográfica v2 — não é permitido reutilizar screenshots de cartões

Após o utilizador rejeitar explicitamente os criativos de 07/11/2026 por fotografias inadequadas e voz acelerada, a via preferencial passou a ser `premium_scene.py` + `auto_site.py`: recolhe apenas o elemento `img.product-card__image`, mede a resolução de origem e parâmetros simples de qualidade, classifica fotografias, recorta as margens identificadas como interfaces incorporadas e compõe fundos da marca com **uma fotografia maior e texto reduzido por plano**. O produto final continua sujeito a crítica estética por IA anfitriã e aprovação humana; pontuações automáticas de cor/contraste **não detetam qualidade publicitária de forma fiável**. Se a página contiver apenas cartazes com textos incrustados ou fotos pobres, não promover um vídeo tecnicamente correto a final: procurar imagens alternativas do próprio site ou sinalizar que faltam fontes visuais adequadas.

A voz do projeto aprovado mantém o **mesmo modelo Piper pt_PT-tugão-medium**, utilizando o parâmetro `--length_scale` superior a 1.0 (mais lento) e pausas entre frases; para cerca de 20s, preferir 35–50 palavras e sem compressão acelerada. `report.json` deve registar `voice_length_scale`, `spoken_words` e duração real. Não chamar humana a uma gravação TTS sintética. A Skill deve **abrir a tira de quadros e pelo menos três quadros individuais de tamanho grande**; um `SUCCESS` no GitHub e o `qa.distinct_scenes_verified` comprovam integridade técnica, não profissionalismo.

## Contrato da IA argumentista — texto e fotografia contam a mesma história

O pedido do proprietário é **ponta a ponta**, sem guião, fotos ou storyboard fornecidos à mão. Em primeiro lugar, **abrir e analisar o negócio**: o que o site vende ou faz, como funciona, para quem é, categorias e características concretas, como consultar produtos/serviços e qual o CTA verdadeiro. Nunca escrever uma frase publicitária sobre uma vantagem que a fonte não comprove. Guardar a fonte em `business_brief.json`: URL, título, descrição do site, conteúdo real, CTA, cores e fotografias candidatas com ID/hash. Consultar `media_candidates.jpg/json` e as páginas de detalhe; não basta copiar uma frase do título do site.

A IA anfitriã **escreve por iniciativa própria um argumento original**, adaptando a publicidade ao contexto. Organizar um gancho, uma explicação do que é o serviço/produto, um desenvolvimento factual ilustrável e a chamada à ação. A fala deve estar próxima da imagem mostrada em cada momento: frase referente ao equipamento A → imagem verificada A; fala sobre comparação → plano real do catálogo/pesquisa; CTA → logótipo e CTA do site. Comentar o produto observado de forma natural, sem ler um catálogo inteiro. A IA cria `voice_sentences` e a seleção de fotos (`preferred_photos` com ID/hash quando necessário) no GitHub depois de analisar os elementos, **sem pedir texto nem fotografias ao utilizador**. O `storyboard.py` obriga a correspondência semântica entre palavras do guião e categoria da foto, e `scene_timing=voice_aligned` usa os tempos medidos pelo Piper no WAV.

**Primeira geração só com URL:** o runner também consegue produzir `business_brief.json`, `storyboard.json` e uma locução fonte-factual via `auto_script`. Esta versão é um *rascunho automático*; **não equivale** ao argumento editorial escrito pela IA anfitriã. Para uma campanha profissional, a IA deve avaliar o briefing, redigir copy própria e relançar o render com storyboard revisto. O utilizador não tem de executar os passos de investigação, escolha, escrita ou revisão.

A duração determina quantos planos diferentes são úteis; **não fixar em três fotos**, nem exigir uma foto por frase. A mesma frase pode acompanhar dois detalhes do equipamento se ambos descreverem o mesmo assunto. A imagem real de uma marca/produto deve manter autenticidade, sem inventar efeitos, descontos ou características. Capturas de ecrã inteiras só quando são o tema da frase (mostrar funcionamento de website), não como substituto de publicidade visual.

**Exemplo de lógica, não texto imposto:** no Low Cost Europa, se o site apresenta tecnologia para estética e opções de produtos, começar por explicar a proposta de descoberta/comparação, depois ilustrar categorias verificadas e terminar com o CTA «VER EQUIPAMENTOS E PREÇOS». Se for uma barbearia ou serviço, construir uma narrativa sobre o serviço real e o modo de marcar, **não** falar de equipamentos de estética. Se for um Reel, primeiro analisar o conteúdo audiovisual original legalmente acessível; aplicar a mesma lógica da narrativa sem fabricar imagens ou fingir acesso.

## Fluxo URL primeiro, sem fotografias manuais

Um pedido público só com URL pode ser criado por GitHub autenticado em martaxi-boss/Criativos-anuncios, caminho ads/requests/NOME-NOVO.json. Exemplo:
    
    {"id":"demo-site-20261107","source_url":"https://example.com/","voice_preference":"approved-piper-pt-PT-tugao-medium","publish":false,"commercial_release":false}

A GitHub Action Criativos-anuncios - gerar video automaticamente é acionada pelo commit na main. O código tools/criativos_anuncios/auto_site.py valida o URL público, tenta abrir Chromium/Playwright, recolhe screenshots de várias secções reais e lê título, textos e CTA visíveis; não inventa imagens de produtos ou faz login. A composição tools/criativos_anuncios/render.py mantém Piper pt-PT e FFmpeg, aceita capture_index correspondente aos PNG daquele run e produz MP4/WAV/report.json. Não publica o anúncio e não utiliza música cuja licença não foi confirmada. O resultado é PREVIEW_ONLY.

Acompanhar o commit e a Action exatos; verificar passos de captura, render, ffprobe, WAV, MP4 e artefacto criativos-anuncios-mp4-voz-qa. A aprovação da voz amostra não substitui a aprovação da nova locução, especialmente de marcas e números. A duração pedida (por exemplo 20 s) é alvo editorial e só se confirma medindo o ficheiro real; não acelerar automaticamente a fala nem cortar palavras.

O conteúdo não confidencial do site pode ser usado como referência; não enviar fotos de clientes, cookies, tokens, vídeos privados ou contas para o repositório público. Manter os ambientes completamente separados: a Action do projeto Criativos executa no próprio runner GitHub e NÃO constitui uma nova capacidade certificada dentro da release Ferrari VPS. Não atribuir o MP4 ao motor Ferrari quando ele não tiver executado.

## Limites e Reels

- Sites e páginas públicas: tentar captação automática e reportar evidência da página real. Não pedir imagens se estiverem disponíveis publicamente e com direitos.
- Facebook, Instagram, TikTok e Reels: verificar se o vídeo original é acessível por método autorizado. A página pública nem sempre disponibiliza o MP4 e pode exigir login. O capturador atual recusa explicitamente tratar uma página social como prova de vídeo obtido. Se não existir uma fonte autorizada, marcar reel_media_pending; não ultrapassar login nem fabricar frames ou legendas.
- Se o domínio estiver inacessível no runner: registar bloqueio DNS, rede, HTTP ou navegador, procurar uma fonte pública alternativa autorizada (p.ex. domínio correto) e não substituir por slides inventados.
- O objetivo é produto editorial de qualidade; screenshots reais e um render válido são apenas uma pré-visualização, não garantia de um anúncio cinematográfico ou final comercialmente aprovado.

## Garantias

A fonte visual confirmada em produção prevalece sobre CSS antigo guardado no GitHub. Preservar cor, logótipo e imagens originais, utilizar 4 a 7 cenas diferentes, legendas, CTA real, movimento moderado e enquadramentos de produto. Distinguir technical_pass, editorial_pending e approved_for_ads; não declarar qualidade profissional ou voz humana natural sem revisão do resultado.
