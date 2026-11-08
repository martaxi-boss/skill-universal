# Certificação real — OpenCV privado integrado no Ferrari (08/11/2026)

## Resultado operacional

- Release ativada: `46b679f4304454e28a23aa779507af393f0c5258`. Fallback preservado: `9004c7a605f15c65d31b08c24bb4511b38a55f92`.
- Catálogo canónico único: `engine/catalog.json` com **173 programas, 274 funções (14 operações + 40 ações + 220 REA), 3 dependências e 2 fornecedores, 452 entradas**.
- A operação `image-analyze` reutiliza OpenCV/NumPy no `/.runtime/venvs/extended/docling/` dentro de `/srv/projects/skill-universal/`, sem instalação global, sem dependência duplicada e sem API paga.
- Teste privado: [pré-teste VPS #42491423623](https://github.com/martaxi-boss/VPS/actions/runs/42491423623), `509` testes PASS, prova de OpenCV via Skill→ZIP, 40/40 executores, 8/8 serviços; `current` permaneceu inalterado.
- Ativação com comutação protegida: [VPS #42491523251](https://github.com/martaxi-boss/VPS/actions/runs/42491523251) PASS, `FERRARI_PRIVATE_ACTIVE_RELEASE=PASS`, `FERRARI_OPENCV_ACTIVE_RELEASE_AND_FALLBACK=PASS`, 509 testes PASS, 8/8 serviços PASS.
- Validador da ponte existente atualizado somente no `ref` pelo [VPS PR #393](https://github.com/martaxi-boss/VPS/pull/393); SSH e transporte não substituídos.

## Prova independente pela Skill instalada/ponte

- Pedido novo público e sintético: `ferrari-requests/job-opencv-live-e2e-20261108-1451.json` no repositório `martaxi-boss/VPS`. Ficheiro de entrada PNG 64×64, 155 bytes, sem dados de utilizador.
- [GitHub Actions #42491707451](https://github.com/martaxi-boss/VPS/actions/runs/42491707451), commit `c1ccf3e3778ed204611a8c0380abfc186eb8ebb7`: `FERRARI_SKILL_JOB_STATUS=completed`, `FERRARI_SKILL_END_TO_END=PASS`, artefacto `ferrari-skill-result-42491707451`.
- Dentro do `response.zip`: `report.json` (`status=completed`, `quality_gate.status=passed`), `artifacts/image-analysis.json` e `artifacts/image-preview.png` com dimensões 64×64 e PNG com assinatura válida. O ZIP foi aberto e verificado fora da execução, incluindo hashes.
- Executor real: `.runtime/venvs/extended/docling/bin/python:opencv-offline`. Versão observada `OpenCV 5.0.0`.
- Hash SHA256 da imagem de entrada: `9d03362c11604e5f5b0f1d6d795350569728c3adebd34d98079908b564ae8750`.
- Hash SHA256 do PNG gerado: `90b97c3863a7f9cac0d2b391a8cdc685d17ce9741f3f0f29b371e6aaef864159`.
- Métricas reproduzidas: brilho 129/255, contraste (desvio-padrão) 30/255, variância do Laplaciano 787,5 (medida no preview).

## Contrato e limites

- `kind=operation`, `operation=image-analyze`, `input={name,content_base64}`; PNG/JPG/JPEG/WebP até 2 MB, imagem descodificada limitada a 24 MP, saída JSON+PNG. Pode exigir `acceptance={"required_extensions":[".json",".png"]}`.
- O worker aplica limites de dimensão no OpenCV antes do `imdecode`, tempo máximo de 90 segundos, caminhos relativos à pasta Ferrari, validação de cabeçalho PNG, hashes e nenhuma execução de shell arbitrário.
- Prova técnica **não** equivale a certificação de qualidade comercial de imagens, modelos de visão computacional avançados, todas as funções do OpenCV, GUI/OBS, formatos PDAL opcionais ou autonomia LLM da equipa Ruflo.
- A atualização da Skill única no GitHub/plugin para v1.0.11 é fonte distribuível; **não** implica que uma instalação ChatGPT específica já tenha sido atualizada. Validar instalação cliente separadamente.

**Sem alterações aos outros projetos ou instalações APT globais para esta integração.**
