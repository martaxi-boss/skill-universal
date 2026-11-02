# Auditoria de entrega — Ferrari Ubuntu 24.04

Data: 2026-11-02. Repositório: `martaxi-boss/skill-universal`.

## Resultado: APTO PARA PRECHECK; NÃO APTO PARA INSTALAR 56/56

**Critério principal:** disponibilidade de um pacote no Ubuntu e compatibilidade garantida com a VPS são proposições diferentes. O catálogo ainda não certifica 56 instalações nem os motores externos.

- **125** candidatos GitHub investigados.
- **56** candidatos pré-selecionados; **34** com pacote APT identificado em runner Ubuntu 24.04 (17 headless, 17 desktop); **22** com documentação/distribuição Linux mas sem teste na VPS.
- **6** identificadores têm revisão de licença aberta no manifesto: `scribus`, `openscad`, `librecad`, `audacity`, `openshot` e `inkscape`.
- **7** operações limitadas disponíveis no motor. Não há executores completos para CAD/BIM/3D, edição audiovisual avançada nem desenvolvimento full-stack.
- **Ruflo/REA** só têm instaladores npm isolados e smoke `--help`; **não** estão integrados operacionalmente ao orquestrador Ferrari.
- **Ghidra 12.2** exige JDK 25; o instalador APT base de 24.04 só prevê openjdk-21. **Não está certificado**.
- **REA 6.8.0** exige Node `^22.23.4 || ^24.22.1 || >=26.12.1`. O Node.js do APT padrão Ubuntu 24.04 **não satisfaz por defeito** o requisito. Não instalar Node global sem isolar o ambiente.
- **JADX 1.5.6** tem ZIP e SHA256 oficiais fixados, mas falta instalação e smoke real.
- Programas GUI (Blender, Krita, CAD, QGIS) podem estar disponíveis via APT mas exigem confirmar CPU/RAM/disco/GUI e o método de execução headless na VPS; não confundir APT com GUI utilizável.
- **Serviços globais `valkey-server` e `prometheus`** foram retirados da instalação APT automática da Ferrari; devem ficar fora do sistema até existir decisão específica sobre conflito de portas, recursos e isolamento.
- **APT Linux** faz dry-run e verificação de candidatos; instalação manual `--apply` recusa pacote ausente, exige Ubuntu 24.04 e simula a resolução APT antes de fazer alterações.

## Etapas e provas exigidas

1. **PRECHECK** (GitHub Actions -> SSH, apenas leitura): Ubuntu, arquitetura, CPU, RAM/disco, Node, Java, executáveis, permissões e conetividade.
2. **DEPLOY** (manual só após PRECHECK PASS): instalar a fonte Ferrari numa pasta exclusiva, executar `doctor` e verificar que os projetos antigos permanecem intactos.
3. **INSTALL_HEADLESS** (manual após DEPLOY PASS): instalação somente dos pacotes gratuitos compatíveis, sem serviços globais e sem Node Ubuntu antigo. Guardar saída `apt-get`, versões e smoke de operações reais.
4. **Motores externos** (fase futura): obter Node compatível isolado, REA, Ruflo, Ghidra com JDK25, JADX com SHA256 e testar operações reais.
5. **Adaptadores profissionais** (fase futura): adicionar e certificar execução por Skill, inclusive CAD/BIM/3D.

## Teste por GitHub Actions sem qualquer instalação

O workflow `.github/workflows/deploy-vps.yml` pode executar **PRECHECK** por `workflow_dispatch`. Foi também acrescentado um gatilho único por `push` ao ficheiro `.github/ferrari-readonly-precheck.request`, **apenas para executar o pré-diagnóstico de leitura**. O gatilho `push` não executa DEPLOY nem INSTALL_HEADLESS.

É obrigatório dispor de secrets SSH em `vps-motor-universal` ou no próprio repositório. Se estiverem em falta, o PRECHECK falha com essa indicação e **não altera o servidor**. Só log real comprovado pode autorizar a fase seguinte.

Referências: `BOOTSTRAP.md`, `engine/ubuntu_selection.json`, `install/external-release-lock.json`, `docs/INSTALACAO_VPS.md`.

**Conclusão:** lançar PRECHECK; não declarar Ferrari 100% funcional nem instalação de 56 ferramentas enquanto não existirem evidências na VPS.

## Resultado da execução de verificação

- CI Ubuntu 24.04: [#41534293244](https://github.com/martaxi-boss/skill-universal/actions/runs/41534293244) — **PASS**.
- PRECHECK via GitHub Actions: [#41534293085](https://github.com/martaxi-boss/skill-universal/actions/runs/41534293085) — **BLOCKED, `MOTOR_SSH_*` secrets absent**. O SSH e qualquer operação na VPS foram ignorados, não houve instalação.
- Ações necessárias: configurar os secrets no repositório independente e voltar a executar PRECHECK, depois DEPLOY e INSTALL_HEADLESS consoante prova real. Nunca afirmar 56/56 certificadas sem teste.
