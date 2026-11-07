# Ferrari — criativos automáticos a partir do site, página ou Reel

Este guia pertence à mesma Skill universal. Usa métodos do projeto independente Criativos-anuncios, mas não instala dependências cruzadas na VPS Ferrari.

## Voz que já está aprovada

O vídeo 1000183150.mp4 (44,8 s; recebido 07/11/2026) mostra o timbre e ritmo de locução que o dono aprovou. O projeto martaxi-boss/Criativos-anuncios utiliza Piper pt_PT-tugão-medium, com modelo verificado por SHA-256, geração de WAV frase a frase e mistura em FFmpeg. **Preferir essa mesma voz**, sem procurar outro TTS nem exigir nova autorização para experimentar o estilo. Não declarar que é uma gravação humana; é síntese pt-PT. A nova locução e sincronismo exigem audição antes de aprovação comercial.

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
