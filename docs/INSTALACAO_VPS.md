# Instalar o Motor Ferrari na VPS Ubuntu — operação real

Este é o procedimento **para a VPS real**, não para o runner GitHub Actions. O código foi criado na branch main do repositório exclusivo \`martaxi-boss/skill-universal\`.

## Fluxo definitivo

\`\`\`text
ChatGPT / Codex / outra IA (interpreta e planeia)
             ↓
     Única Skill Universal
             ↓
       Ligação autenticada
             ↓
     Motor Ferrari na VPS Ubuntu
             ├── Orquestrador independente (engine/orchestrator.py)
             ├── Seleção de ferramentas Ubuntu (engine/ubuntu_selection.json)
             ├── Programas APT aprovados / executores
             ├── Engines externos isolados e verificados (REA/JADX/Ghidra)
             └── Resultados, arquivos e relatório
\`\`\`

**Ferramentas não passam a estar disponíveis por estarem catalogadas.** Para cada uma é preciso comprovar: Ubuntu + arquitetura + versão + licença + instalação + funcionamento + adapter próprio + execução final pela Skill.

## Ligação VPS via GitHub Actions

Workflow manual:
[\`.github/workflows/deploy-vps.yml\`](../.github/workflows/deploy-vps.yml).
Página para iniciar:
[GitHub Actions - Deploy Ferrari](https://github.com/martaxi-boss/skill-universal/actions/workflows/deploy-vps.yml).

Requer, exclusivamente no repositório da Skill Universal, estes **secrets de Actions** (em vez de publicar credenciais):

- \`MOTOR_SSH_HOST\`: endereço do servidor Ubuntu, nunca adivinhar.
- \`MOTOR_SSH_USER\`: utilizador SSH autorizado no servidor.
- \`MOTOR_SSH_PRIVATE_KEY\`: chave privada de ligação SSH.
- \`MOTOR_SSH_KNOWN_HOSTS\`: chave pública do anfitrião SSH validada por via independente.
- \`MOTOR_SSH_PORT\`: opcional, usa 22 se ausente.

Se estiverem definidos noutro repositório, **não** os copiar nem alterar silenciosamente. A ligação só existe após o utilizador a configurar e o workflow completar. Não há execução automática ao fazer push.

O workflow corre sob o ambiente GitHub \`vps-motor-universal\`, com os seus controlos habituais. Selecionar uma fase, escrever \`FERRARI\` no campo de confirmação e iniciar a execução:

| Fase | Efeito |
|---|---|
| \`PRECHECK\` | Liga via SSH e **apenas lê** versão Ubuntu, CPU, RAM, disco, Java, Node, Python, binários e GPU |
| \`DEPLOY\` | Repete PRECHECK, copia fonte para diretório exclusivo e versionado, corre testes e muda o symlink \`current\`; **sem instalar APT** |
| \`INSTALL_HEADLESS\` | Repete PRECHECK e DEPLOY; instala os pacotes APT **aprovados para Ubuntu, sem GUI**, se o utilizador SSH tiver \`sudo -n\`; volta a testar |

Destino único: \`$HOME/.local/share/motor-ferrari/\`, com releases isoladas em \`releases/<commit>\`. Nenhuma fase apaga o REA anterior, Project Leader, Telegram, FADEGO ou outros projetos.

O instalador APT continua com pré-visualização como padrão: \`bash install/ferrari-ubuntu.sh --profile maximum --headless\`. Só a fase \`INSTALL_HEADLESS\` utiliza \`--apply\`.

## Motores externos e fornecedores

O catálogo oficial e as versões selecionadas estão em
[\`install/external-release-lock.json\`](../install/external-release-lock.json):

- **REA 6.8.0, upstream morluto/rea**: instalar isolado com Node.js nas gamas \`^22.23.4 || ^24.22.1 || >=26.12.1\`. Não é o REA antigo da VPS nem partilha a instalação.
- **JADX 1.5.6**: binário CLI do release oficial Linux/cross-platform, com SHA-256 verificado antes de extrair.
- **Ghidra 12.2**: release ZIP oficial, ~570 MB, SHA-256 verificado; requer Java 25 64-bit e espaço adicional para análise.
- **Ruflo 3.71.0**: opcional para orquestração de agentes; não substituir o orquestrador do Motor Ferrari por outro projeto.

Estes motores **não** ficam instalados na fase APT. Precisam de uma fase de instalação controlada, verificação independente de integridade e testes funcionais com entradas reais. Modelos de IA externos precisam de autenticação e podem ter limites; ferramentas livres não garantem modelos remotos gratuitos nem uma GPU disponível.

## Evidência esperada da VPS

Antes de anunciar que o motor está operacional:
1. ID do workflow e commit realmente instalados.
2. Log \`FERRARI_VPS_PREFLIGHT=PASS_READ_ONLY\`, com versão Ubuntu e recursos.
3. \`FERRARI_DEPLOY=PASS_SOURCE_ONLY\` após a cópia e testes.
4. \`FERRARI_APT_SMOKE=PASS\` após ferramentas APT reais.
5. Lista de motores externos instalados, falhas e outputs dos smoke-tests.
6. Teste fim-a-fim: IA → Skill → conexão autorizada → orquestrador → programa na VPS → ficheiro e relatório.

Sem o último teste, a Skill poderá estar preparada, mas **não está ligada operacionalmente à VPS**.

## Comando manual para inspeção, sem instalar

No terminal da VPS Ubuntu, caso já exista acesso e se pretenda apenas diagnóstico:

\`\`\`bash
cd "$HOME/.local/share/motor-ferrari/current"
bash install/ferrari-ubuntu.sh --profile maximum --headless
python3 -m engine.ferrari doctor
\`\`\`

Só executar após implantação do código em \`DEPLOY\`. Para o pré-diagnóstico, usar \`PRECHECK\`, que não exige diretório pré-existente.
