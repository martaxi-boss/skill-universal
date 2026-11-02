# Motor Ferrari — Skill Universal Ubuntu

**[Ler primeiro o BOOTSTRAP — objetivo definitivo, arquitetura, situação real e próximos passos](BOOTSTRAP.md).** É o documento de continuidade de todo o Motor Ferrari, incluindo construção, CAD, BIM e 3D. O catálogo não equivale a software instalado.

**Projeto independente**: a IA anfitriã interpreta e organiza; o Motor Ferrari na VPS Ubuntu seleciona e executa ferramentas próprias. Não depende dos executores de ChatGPT/Codex nem reutiliza Project Leader, REA anterior ou outros projetos.

## Ampliação CAD/3D/Office — novembro 2026

Foram acrescentadas três operações tipadas (`cad-stl`, `blender-house`, `office-pdf`) com adaptadores reais OpenSCAD/Blender/LibreOffice, bem como instalador adicional `install/vps-cad-3d.sh`. **A prova operacional é o GitHub Actions VPS e não apenas a presença das funções no código.** A casa 3D é conceptual, não estrutural ou BIM.

## Instalação real na VPS — 02/11/2026 (mais recente)

**GitHub Actions VPS [#41538472015](https://github.com/martaxi-boss/VPS/actions/runs/41538472015): SUCCESS.** O motor Ferrari foi instalado sob `/home/ubuntu/.local/share/motor-ferrari/current` (release `b8a7de8695b16bf064e0796c3cb9276d3a8254ed`). **41 testes PASS na própria VPS**, execução de HTML/SVG/strings pelo orquestrador, JADX e Ghidra com testes funcionais; REA/Ruflo instalados com smoke de CLI, não com análise/swarm certificados. Node 22.23.4 e Temurin Java 25 estão isolados. A ligação direta da Skill e as 56 ferramentas ainda não estão certificadas. [Ver relatório e evidência](docs/RELATORIO_REAL_VPS_20261102.md).

## Estado da entrega anterior (histórico, ultrapassado pela instalação) — 02/11/2026

**CI Ubuntu 24.04: PASS (#41534293244).** **PRECHECK da VPS: bloqueado (#41534293085)** pela ausência de `MOTOR_SSH_*` no GitHub Actions; sem ligação SSH nem instalação. Ver `BOOTSTRAP.md` e `docs/AUDITORIA_ENTREGA_UBUNTU.md` para retomar.

## Critérios de pré-diagnóstico anteriores à instalação (histórico)

**Não foi comprovada compatibilidade operacional de todas as 56 ferramentas na VPS; não instalar tudo.** O primeiro passo é um **PRECHECK por GitHub Actions, só de leitura**, sem APT nem escrita na VPS. O instalador de pacotes headless exclui Node.js/npm do Ubuntu (versão potencialmente incompatível com REA), serviços Prometheus/Valkey (evitar alterar serviços de outros projetos), recusa pacotes obrigatórios ausentes e testa resolução de dependências APT antes de instalar.

## Workflow manual alternativo no repositório Ferrari (não foi a via usada na instalação real)

O projeto tem agora um [workflow de instalação por fases](.github/workflows/deploy-vps.yml) e um [guia de operação](docs/INSTALACAO_VPS.md). O workflow `workflow_dispatch` é **manual**: PRECHECK (SSH e inspeção real Ubuntu, sem alteração), DEPLOY (código isolado em `$HOME/.local/share/motor-ferrari/`) e INSTALL_HEADLESS (pacotes aprovados, testes e evidência). É necessária ligação SSH configurada nos secrets deste repositório. **Estas fases deste workflow alternativo não foram usadas; a instalação foi efetuada pelo workflow independente do repositório VPS com os secrets existentes.** As 56 ferramentas são uma seleção técnica, não 56 instalações confirmadas.

## Estado operacional em 02/11/2026

- **Orquestrador próprio (novo):** `engine/orchestrator.py` executa planos JSON validados com dependências, etapas paralelas/serie, modo pré-visualização sem alterações, relatório e teste real Ubuntu. Prefect, Ruflo e LangGraph ficam opcionais e não são instalados por defeito.
- **Auditoria de pacotes de Skills (nova):** `engine/skillpacks_audit.json` analisa 9 coleções públicas e 6 possíveis motores; `docs/ORQUESTRADOR_SKILLS_GITHUB.md` explica licença, compatibilidade e seleção, mantendo **uma única Skill**.

- Catálogo GitHub: **125 projetos pesquisados; 56 pré-selecionados com critérios Ubuntu e qualidade** com metadados de estrelas e upstream; catálogo original: **69 entradas**, com sobreposição.
- Motor Ferrari: diagnóstico, roteamento e **sete operações tipadas** (site HTML, cartaz SVG, PDF para texto, redimensionar imagem, thumbnail vídeo, descompilar APK com JADX e strings binárias).
- Integração MCP independente: ferrari_doctor, ferrari_catalog, ferrari_plan, ferrari_run e ferrari_orchestrate, mais pesquisa de alternativas livres.
- Instalador APT Ubuntu 24.04+ por perfis e modo máximo: simulação por defeito; --apply explícito para instalar pacotes compatíveis encontrados.
- **Instalação real comprovada na VPS pelo run #41538472015**; JADX/Ghidra têm testes funcionais e REA/Ruflo smoke CLI. ComfyUI e a ligação direta Skill → motor continuam pendentes. Os testes da runner e os da VPS estão documentados separadamente.

Inclui uma matriz de 18 alternativas legais a aplicações comerciais e pesquisa automática *read-only* de projetos gratuitos no GitHub. O software comercial não é desbloqueado por engenharia reversa.

Consultar [a seleção profissional Ubuntu](docs/SELECAO_UBUNTU.md), [arquitetura e comandos Ferrari](docs/FERRARI.md) e [Skill única](skill/motor-universal-linux/SKILL.md). Ferramentas Adobe pirateadas não são incluídas; existem alternativas gratuitas profissionais.

---

# Motor Universal Linux — projeto independente (protótipo v0.1)

Motor e Skill portáteis para tarefas de desenvolvimento, criação web, criativos, inspeção de aplicações e outras operações numa instalação Linux. **Não reutiliza nem altera** Project Leader, REA FINAL, Ruflo ou qualquer outro projeto do utilizador.

## Arquitetura

```text
ChatGPT / Codex / outros agentes
         |
     Uma Skill (mesmo contrato de instruções)
         |
     Ferramenta nativa ou MCP com ligação autenticada
         |
     Motor Universal Linux (CLI / MCP na VPS)
         |
     Descoberta automática + catálogo + seleção + execução + relatório
         |
     Ferramentas instaladas, REA próprio, modelos/fornecedores disponíveis
```

- **VPS**: motor independente instalado sob uma pasta exclusiva; executa trabalho, não depende de outro repositório. Pode ser invocado pela CLI; o servidor MCP é adaptador opcional, não ativado por defeito.
- **ChatGPT**: a Skill não dá, por si só, acesso SSH à VPS. Precisa de uma ligação autorizada, por exemplo um servidor MCP remoto ou uma ação explícita via GitHub Actions no repositório novo.
- **Codex/Claude/editores**: podem usar a CLI ou o mesmo MCP se o ambiente disponibilizar execução/autenticação. As respetivas interfaces não são idênticas.
- **Sem IA local obrigatória**: a aplicação usa o modelo do agente anfitrião; fornecedores externos gratuitos são opcionais, exigem contas e podem ter quotas. Criativos SVG e sites HTML são gerados no motor sem GPU; criação de imagens fotorealistas não é garantida numa VPS sem GPU ou API.

## O que este pacote já implementa

- Catálogo de ferramentas e fornecedores gratuitos com verificação de presença no host.
- Identificação de perfis Linux (arquitetura, capacidade, comandos).
- Planeamento de tarefas em português/inglês com seleção de capacidade, ferramentas preferidas e alternativas.
- Execução comprovável de três rotas locais: website HTML responsivo, criativo SVG editável e inspeção estática não-invasiva de ficheiros/APKs.
- Ponte MCP opcional para plataformas com cliente compatível.
- Instalador Ubuntu em modo simulação por defeito, com perfis e verificação `apt-cache` antes de instalar.
- Suite de testes para encaminhamento, geração de artefactos e isolamento de projetos.

Este é um **protótipo funcional já instalado na VPS, mas não ainda uma plataforma universal completa**. A implantação completa (REA upstream autónomo, Ghidra, JADX, motores de media, modelos e integrações remotas) exige executar o instalador no Ubuntu e testar cada componente real. Um programa listado não significa que já esteja instalado ou seja compatível com a VPS concreta.

## Testes sem alterar o sistema

```bash
cd motor-universal-linux
python3 -m unittest discover -s tests -v
python3 -m engine.cli doctor
python3 -m engine.cli providers
python3 -m engine.cli catalog
python3 -m engine.cli plan 'criar um site profissional para barbearia'
python3 -m engine.cli run 'criar um site para barbearia' --title 'Barbearia' --output /tmp/universal-demo
python3 -m engine.cli run 'criar criativo para campanha' --title 'Promoção de Outono' --output /tmp/universal-demo
```

## Instalação numa Ubuntu 24.04 isolada

```bash
bash install/install-ubuntu.sh --profile maximum                 # preview, não instala
sudo bash install/install-ubuntu.sh --profile core --apply      # instala só pacote base
sudo bash install/install-ubuntu.sh --profile creative --apply  # instalação de pacotes criativos disponíveis
sudo bash install/install-ubuntu.sh --profile reverse --apply   # análise estática disponível via APT
sudo bash install/install-ubuntu.sh --profile maximum --apply   # todos os perfis APT compatíveis
```

O instalador não apaga nem atualiza outros projetos. Depende de repositórios Ubuntu configurados e de internet. Dependências externas fora do APT são catalogadas para instalação verificada individualmente. O REA oficial requer Node.js compatível, e o motor só pode marcar REA como disponível **depois** de a instalação independente ser comprovada.

## Uso em Codex ou outro agente local

Copiar `skill/motor-universal-linux/SKILL.md` para a pasta de Skills suportada pelo respetivo anfitrião e disponibilizar a CLI `python3 -m engine.cli` dentro do checkout do novo projeto. O ficheiro `integrations/AGENTS.md` fornece compatibilidade no contexto Codex. Usar sempre um checkout independente.

## Uso em ChatGPT

Importar `skill.zip` na área de Skills/Plugins suportada e configurar uma ligação real ao motor (MCP ou ferramenta autenticada) antes de pedir execução na VPS. A Skill orienta o uso da ligação e não promete execução remota sem ela. O Skill ZIP é um artefacto independente do ZIP completo do projeto.

## Licenças e fornecedores

Este protótipo usa apenas código original e não agrega binários nem pesos de terceiros. As ferramentas são inventariadas com os seus upstreams e instaladas separadamente sob as suas licenças. O código deste protótipo é MIT (ver `LICENSE`). Fornecedores com tier gratuito não garantem utilização ilimitada nem estabilidade de preços.

## Segurança e limites operacionais

Sem instalação automática ao receber um pedido; `--apply` é explícito. Sem execução de comandos arbitrários a partir de prompts, SSH implícito, exposição pública de serviços, modificações de projetos antigos ou apagamentos. Entradas de ficheiros são tratadas como dados, não executadas. A engenharia reversa de software exige autorização adequada; este protótipo faz apenas inspeção estática e não neutraliza mecanismos de proteção.

## GitHub Actions independente (modelo incluído)

O workflow `.github/workflows/deploy-vps.yml` usa apenas os quatro secrets `MOTOR_SSH_HOST`, `MOTOR_SSH_USER`, `MOTOR_SSH_PRIVATE_KEY`, `MOTOR_SSH_KNOWN_HOSTS` (e `MOTOR_SSH_PORT` opcional). Requer um repositório GitHub **novo** e autorização `workflow_dispatch` com `DEPLOY`. Copia o motor para `$HOME/.local/share/motor-universal-linux`, corre testes/doctor e não instala pacotes do sistema. Confirmação do host SSH via known_hosts é obrigatória. Estes secrets são necessários **apenas para este workflow alternativo**. A instalação real usou a credencial SSH previamente configurada no repo `martaxi-boss/VPS`, através de um workflow dedicado que não alterou os antigos.

## REA e Ruflo no mesmo projeto, mas com instalações independentes

O script `install/install-agent-engines.sh` instala opcionalmente `rea-agents@6.8.0` e `ruflo@3.71.0` em duas pastas separadas dentro da nova instalação; não liga nem altera projetos antigos. É **pré-visualização por defeito**, requer Node.js compatível (22.19+, 24.11+ ou 26+) e `--apply` explícito. O teste `--help` confirma apenas que as CLIs arrancam, não certifica os motores internos, Ghidra, os fornecedores, o Codex nem ChatGPT.

```bash
bash install/install-agent-engines.sh --profile all       # ver o que se instalaria
bash install/install-agent-engines.sh --profile all --apply
python3 -m engine.cli doctor
```