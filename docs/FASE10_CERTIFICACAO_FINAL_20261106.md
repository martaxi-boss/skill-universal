# Ferrari — Ponto 6: certificação técnica (06/11/2026)

**Estado: PASS para o motor e a ponte GitHub–VPS. Fecho administrativo global ainda condicionado.** Não atribuir 10/10 ou afirmar remoção de aplicações globais do Ubuntu sem provas adicionais.

## Provas reais

- **CI:** [GitHub #42201645937](https://github.com/martaxi-boss/skill-universal/actions/runs/42201645937), SUCCESS: 308 testes PASS e empacotamento da Skill única. Após esta documentação, usar a nova CI para obter a versão atualizada do ZIP.
- **VPS privada:** [#42207839068](https://github.com/martaxi-boss/VPS/actions/runs/42207839068), SUCCESS: pasta /srv/projects/skill-universal; release a266b25e06a9c8acf1fdc940d22b99070cd17ded ativa; fallback 758e1b435317fa26277b332b75bc47c67910be81 presente; catálogo 40 ações; motor e orquestrador próprios preservados.
- **Integridade:** SHA-256 verificado dos três pesos SafeTensors Stable Diffusion 1.5 (UNet, CLIP, VAE) e do modelo CTranslate2 faster-whisper tiny. Prova real de imagem CPU [#42149365272](https://github.com/martaxi-boss/VPS/actions/runs/42149365272) e transcrição CPU [#42170510453](https://github.com/martaxi-boss/VPS/actions/runs/42170510453).
- **Serviços protegidos:** 8/8 ativos (PINK IPTV backend, VPN PINK, FADEGO, Low Cost Europa, os dois robôs PM2, Nginx e PostgreSQL). Sem alteração de outro projeto e sem instalação global.
- **Recursos:** cgroup v2 presente, os testes reais de ComfyUI e faster-whisper tinham limites de memória e CPU em escopos temporários. Isso não certifica limites universais para todas as 40 ações. Nenhum daemon coordenador Ruflo indevido detetado.
- **Ponte original:** [VPS #42207928270](https://github.com/martaxi-boss/VPS/actions/runs/42207928270), SUCCESS. Pedido novo kind=invoke para file-mime, com JSON sintético: status=completed, FERRARI_SKILL_RESPONSE_ZIP=PASS e FERRARI_SKILL_END_TO_END=PASS. O artefacto real foi descarregado: response.zip contém report.json e artifacts/mime.txt = application/json, executado pelo file privado do Ferrari.
- **Inventário atual:** [#42200976757](https://github.com/martaxi-boss/VPS/actions/runs/42200976757), 40/40 ações invocáveis e 47/56 candidatos detetados. Invocabilidade não é certificado de cada função opcional.
- **Higiene P5:** [auditoria #42200744741](https://github.com/martaxi-boss/VPS/actions/runs/42200744741), zero resíduos nos caminhos de testes Ferrari conhecidos, oito componentes privados, oito serviços ativos. [PR #80](https://github.com/martaxi-boss/skill-universal/pull/80) registou a classificação e preservou os outros projetos.

## Pendências que não são ocultadas

1. **Fase 9 transversal:** 16 pacotes APT globais ainda instalados (8 sem cópia privada certificada), resíduos externos sem titularidade/comprovação de consumidores, alterações locais de PINK IPTV e IPTV VPN Bot preservadas. Não executar apt purge, reset ou deploy cruzado sem revisão própria desses projetos e rollback.
2. **Skill instalada no cliente:** o GitHub e a CI contêm a fonte atualizada da Skill única e um ZIP; o plugin instalado no ChatGPT apresentava instruções mais antigas. A atualização desse mesmo plugin exige identificação de backend e direitos de edição. Nunca criar uma Skill duplicada para contornar a dificuldade. Preparar e entregar o ZIP; não declarar que está instalado automaticamente.
3. **Capacidades opcionais:** multiagentes Ruflo com modelo/fornecedor, GPU, Penpot e GUI integral não certificados. Limites duros globais CPU/RAM também não certificados além dos casos verificados.

## Veredito

**PASS técnico: Ferrari operacional, privado e ligado ao GitHub, com fallback, 40 ações, pesos verificados e resultados reais.** A certificação global 100% continua condicionada às pendências externas e à atualização real da Skill no cliente. Nenhum fornecedor pago obrigatório, nenhum coordenador na VPS e nenhuma alteração dos outros projetos.
