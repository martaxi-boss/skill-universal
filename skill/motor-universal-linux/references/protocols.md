# Protocolos profissionais do Motor Ferrari

Este ficheiro complementa a **única Skill Universal**. Não invocar Skills
externas nem inventar executores. O motor Ubuntu é a fonte de verdade.

## Escolha por tipo de tarefa

| Domínio | Primeiro executor gratuito a avaliar | Alternativas | Teste obrigatório |
|---|---|---|---|
| Sites e aplicações | Next.js / Vite, conforme projeto | Astro, Bootstrap, Tailwind, Penpot | build, browser real com Playwright, acessibilidade, navegação |
| Loja online | stack web+backend open-source | Saleor/Medusa sob análise, apenas se Ubuntu permitir | autenticação, encomendas e testes de integração antes de produção |
| Design raster | GIMP / Krita | ImageMagick/libvips para lote | exportar PNG/JPEG, dimensões e verificação visual |
| Design vetorial | Inkscape | SVG local / Penpot | SVG válido e export PDF/PNG |
| 3D/animação | Blender headless / OpenSCAD | Synfig, OpenToonz (GUI) | abrir, renderizar, formatos, tempo e memória |
| Engenharia reversa | REA independente + Ghidra | JADX, Apktool, Binwalk, radare2 | hash do alvo, resultado por ferramenta, relatório |
| Documentos/PDF | LibreOffice headless, Pandoc | Docling, OCRmyPDF, Typst, Tesseract | layout renderizado e verificação de páginas |
| Vídeo/áudio | FFmpeg/FFprobe | Kdenlive, Audacity, Whisper, Piper | duração, codecs, resolução e inspeção final |
| Dados | DuckDB / Polars | Pandas, Streamlit, Gradio | validação de esquema e comparação com amostras |
| CAD/cartografia | FreeCAD AppImage / QGIS | OpenSCAD, LibreCAD | export e reabertura do ficheiro |
| Workflows | Ferrari DAG; Prefect opcional | LangGraph, Ruflo só se necessário | dependências, erros, estado e registo de artefactos |

Cada linha descreve candidatos: **não implica instalação**. Consultar
\`engine/ubuntu_selection.json\` para versões, licença e estado Ubuntu.

## Roteamento pela Skill

1. Entender tarefa, entradas e o resultado que deverá ser entregue.
2. Consultar \`ferrari_doctor\`, \`ferrari_plan\` e seleção Ubuntu.
3. Se o pedido exige várias ferramentas, construir plano DAG tipado,
   validar e pré-visualizar no orquestrador Ferrari.
4. Selecionar executores já certificados, preferindo opções locais
   e realmente gratuitas. Se faltam, consultar a auditoria do GitHub.
5. Nunca executar um script de Skills de terceiros só por estar numa
   coleção popular. Inspecionar dependências, licenças e efeitos.
6. Só enviar plano de execução com autorização e ligação real à VPS.
7. Confirmar saídas com testes objetivos e indicar o executor utilizado.

## Padrões assimiláveis de coleções públicas

- **Agent Skills**: uma entrada \`SKILL.md\` e referências carregadas por
  domínio, para reduzir o contexto do modelo.
- **Superpowers**: definir resultado, decompor trabalho, testar e rever.
- **wshobson/agents**: papéis especializados só como guias de análise;
  sem exigir plugins/hook do host.
- **Vercel Skills**: opcionalmente pesquisar novos procedimentos;
  não instalar indiscriminadamente outras Skills.
- **Anthropic Skills**: aceitar só exemplos sob licença adequada,
  nunca importar Skills documentais apenas source-available.

Estes são padrões originais Ferrari derivados da análise pública;
nenhum ficheiro de terceiro foi copiado neste módulo.

## Orquestração e níveis de fiabilidade

- **Agora**: DAG de tarefas tipadas, pré-visualização sem efeitos,
  execução Ubuntu, serial/paralelo, logs e propagação de falhas.
- **Por certificar**: Prefect autoalojado, agendamento, retries,
  recuperação de trabalho após reinício, monitorização contínua,
  GPUs e modelos, ligação remota ponta a ponta.
- **Nunca prometer 100%** sem casos reais em cada domínio da VPS.
