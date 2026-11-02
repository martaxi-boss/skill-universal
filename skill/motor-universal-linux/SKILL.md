---
name: motor-universal-linux
description: Orquestrar tarefas criativas e técnicas num motor Linux autónomo, incluindo criação de sites e layouts, criativos/imagens, engenharia reversa de APK e binários, programação, dados e documentos. Usar quando o utilizador invocar Motor Universal Linux para executar ou planear tarefas através de ChatGPT, Codex ou outro cliente com CLI/MCP disponível. Selecionar automaticamente ferramentas locais gratuitas compatíveis e fornecedores gratuitos configurados, sem confundir catálogo com instalação real.
---

# Motor Universal Linux

Trabalhar exclusivamente no novo projeto independente `motor-universal-linux`. A Skill é o ponto único de entrada; o motor na VPS ou no anfitrião executa apenas através de ligação verificada e autorizada.

## Protocolo obrigatório

1. Interpretar o pedido natural, incluindo pedidos ditados, e identificar objetivo, entradas e resultado concreto (ficheiros, explicação, auditoria ou aplicação).
2. Detetar que executores reais existem no contexto atual: `motor_*` via MCP autenticado, CLI do novo projeto, ou ferramentas nativas apropriadas do anfitrião. **A Skill sozinha não cria acesso à VPS.**
3. Pedir ao motor `motor_health`/`doctor`, `motor_catalog` e `motor_plan` antes de iniciar uma tarefa remota. Confirmar sistemas, versão, ferramentas instaladas, recursos e requisitos.
4. Selecionar a ferramenta gratuita compatível de maior adequação, e considerar fornecedores externos gratuitos *apenas* se disponíveis e autenticados. Distinguir open-source sem custos de APIs com quotas gratuitas. Nunca cair silenciosamente num fornecedor pago.
5. Executar com o motor real quando ele disponibilizar a rota. Caso contrário, usar ferramentas nativas realmente disponíveis ou relatar precisamente a parte indisponível. Nunca marcar uma integração como testada apenas por constar no catálogo.
6. Devolver artefacto final ou evidência técnica: executor usado, saídas, versão, testes, erros e limitações. Nunca afirmar que a VPS foi modificada sem logs de execução genuínos.

## Encaminhamento por tipo de tarefa

- Website/loja/layout: preferir template local apropriado, componentes de layout livres e projeto responsivo; conferir funcionamento e acessibilidade.
- Criativo/imagem: escolher edição/composição gráfica local para SVG/artefactos, ferramenta de imagem do anfitrião se disponível, ou modelo gratuito autenticado. Não confundir SVG tipográfico com geração de imagem fotorealista.
- APK/binário/firmware: detetar formatos e selecionar REA Linux próprio, Ghidra, JADX, Apktool, binutils ou outros programas realmente instalados. O REA do novo projeto tem instalação isolada. Inspecionar o alvo sem executá-lo por defeito. Não garantir recuperação de código-fonte original.
- Programação/testes/dados/documentos/vídeo: selecionar ferramentas correspondentes efetivamente disponíveis e produzir testes verificáveis. Funções catalogadas mas não implementadas requerem um executor adequado no anfitrião.
- Orquestração: Ruflo é opção de investigação/integração do novo projeto, não gestor ativo por pressuposto; não inicializar em repositórios antigos.

## Comandos CLI (quando existe checkout local)

- `python3 -m engine.cli doctor`
- `python3 -m engine.cli catalog`
- `python3 -m engine.cli providers`
- `python3 -m engine.cli plan 'criar um site para barbearia'`
- `python3 -m engine.cli run 'criar um site' --title 'A Minha Empresa' --output /caminho/de/saida`
- `python3 -m engine.cli run 'criar um criativo' --title 'Promoção' --output /caminho/de/saida`
- `python3 -m engine.cli run 'descompilar APK' --input /caminho/app.apk --output /caminho/de/saida` (inspeção estática básica, **não** descompilação completa)

Não executar instalação Linux automaticamente apenas por receber uma tarefa. Instalar apenas os componentes necessários e aprovados após diagnóstico da VPS.

Ler [references/workflows.md](references/workflows.md) para as ligações por anfitrião, estados de instalação e capacidades efetivamente implementadas. Consultar o catálogo `engine/catalog.json` no checkout da VPS como fonte primária, não valores memorizados nesta Skill.
