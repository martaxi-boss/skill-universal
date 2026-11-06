> **NOTA DE HIGIENIZAÇÃO (03/11/2026): documentação histórica ou de procedimento, não fotografia atual da VPS.** Para release, contagens, REA próprio, Apktool 3.0.3 e pendências reais, consultar primeiro [BOOTSTRAP.md](../BOOTSTRAP.md), confirmado pelos runs [#41671631900](https://github.com/martaxi-boss/VPS/actions/runs/41671631900) e [#41672372249](https://github.com/martaxi-boss/VPS/actions/runs/41672372249). Referências nesta página a instalações pendentes, versões antigas ou ligação não certificada descrevem etapas passadas; não executar instalações automaticamente.

# Seleção profissional — Motor Ferrari / Ubuntu 24.04

> **Revisão de 06/11/2026:** Penpot retirado da seleção ativa e do catálogo único, por decisão do proprietário, por não ter sido instalado e exigir uma pilha mais pesada de contentores. OpenPencil permanece como integração privada Ferrari. No inventário da release anterior, [#42286932312](https://github.com/martaxi-boss/VPS/actions/runs/42286932312), 55/56 candidatos estavam detetados; a seleção revista tem 55 candidatos. Isto não certifica automaticamente todas as operações.

**Data da auditoria:** 2 de novembro de 2026. **Âmbito:** apenas o projeto independente `martaxi-boss/skill-universal`, sem alterações à VPS nem a outros projetos.

## Objetivo

Uma única Skill pessoal recebe orientações de qualquer IA e utiliza **apenas** programas próprios do motor Ubuntu. O catálogo não serve para impressionar com números: serve para escolher ferramentas de alta qualidade sem instalar pacotes inúteis ou incompatíveis.

## Resultados

- **125 projetos públicos** já inventariados no GitHub; *não* são 125 ferramentas instaladas nem aprovadas.
- **55 atualmente selecionados para análise técnica de Ubuntu**, no único `engine/catalog.json` (originalmente 56, antes de retirar Penpot).
- **34 candidatos APT confirmados num runner Ubuntu 24.04** (17 aplicações headless + 17 gráficas; a contagem deve ser reconfirmada sempre que a matriz mudar). *APT disponível não significa execução funcional.*
- **21 candidatos com via Linux upstream**, sujeitos a instalação de versão fixa e testes de dependências/hardware. Inclui FreeCAD AppImage, REA, Ghidra, JADX e frameworks web/dados.
- **Zero ferramentas instaladas ou certificadas na VPS neste processo.**

Fontes verificáveis:
- [Ubuntu 24.04 APT headless e GUI](https://github.com/martaxi-boss/skill-universal/actions/runs/41527000386)
- [Pacotes APT adicionais: Inkscape, Audacity, LibreCAD, OpenSCAD, OpenShot; FreeCAD ausente do APT configurado](https://github.com/martaxi-boss/skill-universal/actions/runs/41527450172)
- [Lista técnica selecionada com licença, dependências e estado](../engine/catalog.json)

## Gates obrigatórios, aplicados por programa

1. **Fonte e manutenção.** Upstream oficial, releases ativas, comunidade, histórico, segurança e *stars* como sinal secundário.
2. **Licença e custo.** Livre para uso pessoal/profissional; verificar obrigações e licenças de pesos/modelos. Serviços gratuitos com quota **não** equivalem a capacidade ilimitada.
3. **Ubuntu.** Documentação oficial Linux e um dos caminhos: pacote APT do Ubuntu 24.04, AppImage oficial, release Linux verificável, container oficial compatível, ou instalação Python/Node documentada. Nada de ferramentas Windows/macOS apenas.
4. **Dependências.** Node/JDK/Python compatíveis; arquitetura x86_64/aarch64; runtime X/Wayland, drivers, RAM, disco e GPU, conforme cada caso.
5. **Execução real.** A ferramenta só passa de *candidata* para *operacional* depois de instalada na VPS e de gerar resultado com um caso de teste conhecido. Programas gráficos precisam de automação ou sessão gráfica funcional.
6. **Integração.** O motor tem de possuir um adaptador próprio que selecione/executa a ferramenta e devolva artefactos. Estar catalogado não dá ao modelo capacidade de executar o programa.

## Grupos prioritários

| Área | Ferramentas selecionadas, não necessariamente instaladas | Via Ubuntu |
|---|---|---|
| Reverse / Android / firmware | REA, Ghidra, JADX, Apktool, Binwalk, radare2 | APT + releases oficiais; Ghidra: JDK 25 |
| Web e layouts | Next.js, Vite, Tailwind, Bootstrap, Playwright, shadcn/ui | Node por projeto; Playwright suporta Ubuntu 24.04; OpenPencil tem CLI privada Ferrari, fora desta seleção Ubuntu original |
| Imagens e design | GIMP, Krita, Blender, Inkscape, ImageMagick, libvips | APT/versões Linux; GUI a verificar |
| Vídeo e áudio | FFmpeg, Kdenlive, Audacity, OBS, faster-whisper, LMMS | APT / Python; GUI e memória |
| Escritório e PDF | LibreOffice, Pandoc, Tesseract, OCRmyPDF, Docling, Typst, Scribus | APT / Python/CLI; Docling pode usar CPU |
| CAD e mapas | FreeCAD, OpenSCAD, LibreCAD, QGIS | APT ou AppImage Linux oficial |
| Dados e aplicações | DuckDB, Polars, Streamlit, Gradio, Valkey | Python/venv e APT |
| Infra, agentes, métricas | Ansible, Prometheus, Ruflo, Prefect | APT ou runtime próprio; Ruflo é opcional |
| IA visual | ComfyUI | Só se hardware e modelos permitirem |

### Dependências que não se podem confundir

- **Ghidra 12.2:** documentação oficial exige **JDK 25 64-bit**. A presença de Java 21 na VPS não o certifica. [Ghidra Docs](https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/GettingStarted.md)
- **REA:** exige Node.js **22.23.4+ da série 22**, **24.22.1+ da série 24** ou **26.12.1+**; é preciso confirmar a versão instalada e os fornecedores disponíveis. [REA instalação](https://github.com/morluto/rea/blob/main/docs/installation.md)
- **JADX:** Java 11 ou superior e CLI Linux do ZIP oficial. [JADX](https://github.com/skylot/jadx/blob/master/README.md)
- **Krita/Kdenlive:** exigem ambiente gráfico para as funcionalidades interativas. [Krita](https://krita.org/en/download/), [Kdenlive](https://docs.kdenlive.org/en/getting_started/installation.html)
- **Blender:** permite renderização em segundo plano (`--background`), mas recursos e aceleração dependem da tarefa. [Blender](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
- **FreeCAD:** não obteve candidato APT no runner; dispõe de AppImage Linux oficial. Não substituir por download de terceiros. [FreeCAD](https://www.freecad.org/downloads.php?lang=us)
- **Playwright:** suporte oficial Ubuntu 24.04, mas navegadores e bibliotecas adicionais têm de ser instalados e testados. [Playwright](https://playwright.dev/docs/intro)
- **Docling:** instalação Linux com variante CPU, mas modelos e dependências exigem memória/disco. [Docling](https://docling-project.github.io/docling/getting_started/installation/)

## Exclusões e pendências de investigação

- A lista histórica de 125 projetos tinha 69 não selecionados inicialmente; Penpot foi agora retirado da candidatura. Novos candidatos só entram mediante provas acima.
- Programas gráficos e ferramentas de GPU não são automaticamente executáveis numa VPS Ubuntu Server sem display/GPU.
- Não utilizar cópias adulteradas para contornar pagamentos/licenças como se fossem software livre. É possível usar engenharia reversa legítima para interoperabilidade e alternativas independentes.
- Repositórios com licenças ambíguas permanecem em revisão, e não entram no plano de instalação automática.
- O instalador usa *dry-run* e confere APT na máquina destino; **não** equivale a certificação de produção.

**Próxima fase:** medir CPU, RAM, armazenamento, arquitetura e interface da VPS real; só depois instalar as opções selecionadas e executar testes de ponta a ponta. Até lá, não escrever na VPS.
