# Ferrari — criativos de qualquer fonte autorizada

**Regra permanente (07/11/2026): a Skill Ferrari não é um conversor de URLs.** O utilizador entrega aquilo que tiver: site, fotografias, vídeo, Reel, página, descrição ou combinação de fontes. A IA anfitriã cria conceito, texto, escolha de imagens, locução e montagem; não exige materiais que o utilizador não tenha.

## Modalidades de entrada

| Entrada | Análise | Criativo |
|---|---|---|
| URL de site/página | Negócio real, funcionamento, imagens, identidade e CTA | Campanha inspirada na marca com fotografias reais |
| Fotografias anexadas | Conteúdo visual, qualidade, enquadramentos e contexto factual | Argumento original, cenas visuais e voz sincronizada |
| Vídeo enviado | Duração, melhores momentos, imagens e áudio autorizado | Reedição dos momentos com narração, legendas e transições |
| Reel / link social | Vídeo original anexado ou acesso legítimo ao conteúdo | Versão adaptada; não contornar login nem inventar acesso |
| Ideia / texto livre | Conceito e factos fornecidos | Storyboard e media ilustrativa, sem fingir fotografia de produto real |
| Mistura (site+fotos+vídeo) | Cruzar proveniência e resolver eventuais contradições | Uma narrativa coerente com todos os materiais úteis |

A **duração** define o ritmo e o número apropriado de planos; 20 s pode ter 5–7 planos, 45 s 10–15, sem números fixos. O guião explica o que se vê. Uma frase pode acompanhar várias fotografias do mesmo assunto; não colocar imagens desconexas e não acelerar a voz só para caber.

## Contrato de criação normalizado

A IA interpreta a entrada e escolhe o adaptador sem obrigar URL:

- `input_kind`: `website`, `photos`, `video`, `reel`, `text_brief` ou `mixed`.
- `sources`: ficheiros ou URLs reais, proveniência e permissões, distinguindo media pessoal privado de web pública.
- `output`: `video_ad`, `reel`, `story`, `static_ad` ou `carousel`.
- `editorial_brief`: o que o negócio realmente oferece e o objetivo da publicidade.
- `voice_script`: texto criado pela IA anfitriã, em pt-PT, adequado aos produtos/serviços vistos.
- `storyboard`: cada frase ligada a uma fotografia/clipe relevante, origem e tempos de áudio.
- `technical_status`, `editorial_status` e `rights_status`: verificar separadamente. MP4 válido não significa qualidade comercial aprovada.

**Direção criativa:** primeiro inspecionar a fonte e perceber o que se anuncia; depois escrever argumento original (gancho, explicação, exemplos e CTA), escolher media de qualidade que ilustre cada frase, montar e escutar. Não pedir ao utilizador que escolha fotografias ou escreva texto se houver contexto suficiente. Não inventar descontos, preços, características técnicas, testemunhos ou vendas.

## Ficheiros anexados: pré-processamento local privado

O repositório independente `martaxi-boss/Criativos-anuncios` inclui `tools/criativos_anuncios/media_intake.py`, que aceita PNG/JPG/WEBP e MP4/MOV/M4V/WEBM **locais e autorizados**. No contexto privado onde os ficheiros estão materializados, usa Pillow/FFprobe/FFmpeg para verificar fontes, extrair fotogramas e produzir:

- `intake_manifest.json` — proveniência, tipos, duração, hashes e direitos por confirmar;
- `media_candidates.jpg` — painel com todas as fotografias e fotogramas candidatos;
- `work/scene_NN.png` — imagens reais normalizadas a 9:16 para pré-visualização.

Exemplo com dois ficheiros locais que foram autorizados pelo utilizador:

`python tools/criativos_anuncios/media_intake.py --input /privado/foto.jpg --input /privado/video.mp4 --output-dir /privado/preview`

A IA **tem de ver** imagens e vídeo fornecidos, escrever o texto adaptado e preencher um storyboard privado com `voice_sentences` e `shots[].candidate_id`, `shots[].voice_index` e `shots[].visual_caption`. O script aceita depois `--storyboard /privado/storyboard.json` para criar `render_request.json` e os PNG com hashes verificados. O renderizador existente aceita esses PNG com `--cached-assets` e produz uma pré-visualização com o Piper pt_PT-tugão-medium **apenas depois de execução real**.

**Limite honesto:** o pré-processador de vídeo atual extrai frames, não preserva ainda excertos de vídeo em movimento no resultado. Uma montagem verdadeira de trechos exige um fluxo de FFmpeg/MLT adicional, a validar separadamente. Nunca rotular sequências de fotogramas como edição cinematográfica de clips contínuos.

## Website e redes sociais

Para um site público, usar o capturador já testado e o guia [automatic-creative-from-url.md](automatic-creative-from-url.md). Para fotografias/vídeo privados, nunca enviar os bytes para um repositório GitHub público: trabalhar no ambiente privado da conversa ou num destino privado expressamente autorizado. Um Reel sem media original acessível e permissão não é descarregável automaticamente só com um link; comunicar essa limitação.

## Exemplos sem trabalho manual para o utilizador

- «Faz um Reel de 20 segundos com este site». → Análise real, texto e visuais.
- «Estas seis fotografias são do meu salão: cria publicidade de 30 segundos». → Inspecionar fotografias, escrever guião e montar.
- «Deste vídeo de um minuto, faz 20 segundos». → Analisar vídeo e selecionar momentos; preservar movimento se disponível editor certificado.
- «Usa estas fotografias, um vídeo e o site». → Unificar mensagem, marca, media e locução.
- «Tenho apenas esta ideia». → Criar conceito e imagens declaradamente ilustrativas, nunca falsas provas de produto.

**Aprovação:** voz pt-PT de referência Piper aprovada em estilo, mas cada locução nova precisa de escuta; media e música exigem direitos comerciais; resultado marcado como prévia até revisão editorial. Não declarar entrega sem ficheiro verificado e não afirmar que o Ferrari VPS executou quando foi o projeto independente ou o ChatGPT.
