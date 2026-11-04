# Ferrari — Hopper privado, sem instalação global

**Projeto GitHub:** `martaxi-boss/skill-universal`  
**Raiz física Ubuntu:** `/srv/projects/skill-universal`

O Hopper Disassembler é software proprietário da Cryptic Apps. O fornecedor permite demonstração oficial sem licença paga; **esta instalação NÃO está ativada com uma licença comercial**. O pacote executável não pode ser distribuído pelo repositório público. No GitHub ficam o instalador, a integração e os testes, nunca o binário comercial nem chaves de licença.

## Instalação isolada

- `install/vps-hopper-private.py` obtém o pacote oficial Linux Ubuntu/Mint em HTTPS.
- A versão verificada é `6.6.1`. Valida SHA-1 do pacote, assinatura PGP do editor e SHA-256 do executável antes de extrair, sem executar scripts DEB ou instalar pacotes via APT.
- Chave primária do fabricante: `7C2D73BAFAF5B9A710A69DA1A26DF815099B1BCD`.
- Executável: `/srv/projects/skill-universal/tools/hopper-6.6.1/opt/hopper/bin/Hopper`.
- A assinatura, o pacote original e o manifesto de prova permanecem dentro da instalação privada em `private-provenance/`.
- `engine/rea_mcp.py` atribui `HOPPER_LAUNCHER_PATH` exclusivamente a esse executável; ignora variáveis globais herdadas. Se o programa não estiver instalado, as restantes ferramentas REA continuam funcionais.

**Teste de origem real:** [VPS run #41921893982](https://github.com/martaxi-boss/VPS/actions/runs/41921893982) confirmou o pacote oficial assinado, sem bibliotecas partilhadas em falta. **Doctor real:** [#41922087539](https://github.com/martaxi-boss/VPS/actions/runs/41922087539) encontrou `hopper`, `hopper-version` e `hopper-demo-runtime` saudáveis. Isto não comprova licença comercial nem análise completa de qualquer binário.

### Limites

A demo oficial tem sessões de 30 minutos, sem guardar/exportar projetos e com depurador desativado. Uma ativação comercial exige uma licença adquirida legitimamente e um processo privado; nunca colocar chave no GitHub, no transporte Ferrari ou nos logs. Consultar o fabricante em https://www.hopperapp.com/download e https://www.hopperapp.com/license_agreement.html.

A instalação global obsoleta `hopper 6.6.0` não é necessária para o Ferrari. Só eliminar esse pacote após confirmar a instalação privada e que a simulação do gestor de pacotes não remove componentes de outros projetos.

**Nota sobre a regra das pastas:** a instalação do Hopper e dos seus dados específicos é privada do Ferrari. O Ubuntu continua a precisar dos seus próprios binários de sistema (systemd, SSH, bibliotecas básicas), o que não equivale a uma instalação extra do Hopper nem a partilha de projetos.
