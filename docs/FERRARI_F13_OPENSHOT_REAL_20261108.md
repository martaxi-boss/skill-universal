# Ferrari F13 — OpenShot 4.1.1 edição e exportação reais (08/11/2026)

## Evidência de execução

**[VPS F13 final #42513141634](https://github.com/martaxi-boss/VPS/actions/runs/42513141634) — SUCCESS / PASS.** Foi descarregado e aberto o ZIP do artefacto `ferrari-universal-42513141634`; o JSON `ferrari-universal-report.json` foi validado na conversa. O procedimento está no único repositório Ferrari, [`install/vps-f13-openshot-headless-certify.py`](../install/vps-f13-openshot-headless-certify.py), commit corrigido `19073c231532f03d28f7af4a769dd5687b3d8bf4`. Invocação autorizada através do [workflow existente VPS PR #409](https://github.com/martaxi-boss/VPS/pull/409), sem uma segunda ponte ou modelo por agente.

| Verificação | Resultado observado |
|---|---|
| Release Ferrari ativa | `3f0ba44b7d8475a74a63c6010d1e27063c04bf1e` |
| Fallback preservado | `427e1c33c6d10ca8ecd2103861adccd3d552c381` |
| Executável | `tools/openshot-4.1.1/squashfs-root/AppRun` privado |
| Entrada | MP4 **sintético**, 167 421 bytes, **2,0 segundos** |
| Comandos efetivos | `file import`, `project profile`, `clip add`, `project save`, `export start` |
| Edição | Corte do clip na timeline para **1,0 segundo** |
| Projeto editável | **34 394 bytes** em `.osp` |
| SHA-256 OSP | `09521229021c033d4caa5cadf6ca74851fdd10f1c757880c3db6a7240e6a7db2` |
| Vídeo exportado | **239 341 bytes** em `.mp4` |
| SHA-256 MP4 | `506cff9aebd51f5a11475f29e4d7d96c479a3ea95089f7f4e8a34fd370979a4f` |
| FFprobe real | Duração **1,0 s**, resolução **320×180**, stream de vídeo presente |
| Serviços de outros projetos | **8/8 ativos**, antes e depois |
| Alterações APT, projetos externos | **Não** |
| Media/Internet externas | **Não** |
| Diretórios permanentes adicionados | **Não** |

Os dados de teste permaneceram em `.runtime` temporário e foram eliminados após a leitura. **O ZIP do workflow contém o relatório, não cópias persistentes do MP4/OSP.** O SHA-256 prova a identidade dos ficheiros gerados no teste, mas não permite recuperá-los após a remoção deliberada do temporário.

## Rastreabilidade das correções

1. [Prova preparatória #42512655839](https://github.com/martaxi-boss/VPS/actions/runs/42512655839): CLI privada confirmou comandos `session`, `clip` e `export`, **sem** certificação funcional nessa etapa.
2. [Primeiro ensaio real #42512732329](https://github.com/martaxi-boss/VPS/actions/runs/42512732329): **BLOCKED** após importação verdadeira, porque o OpenShot devolve os IDs em `result.data.id`, e o primeiro teste só procurava IDs no nível superior.
3. [Correção Ferrari PR #173](https://github.com/martaxi-boss/skill-universal/pull/173): leitura de IDs aninhados estritamente validada + teste de regressão com estrutura obtida da VPS; CI push #42512875331 e PR #42512891366 SUCCESS.
4. [Entrega VPS PR #409](https://github.com/martaxi-boss/VPS/pull/409): pedido novo `universal-f13-certify-r2-20261108.json`, revisão imutável corrigida, identidade SSH e rollback inalterados.
5. [Repetição real #42513141634](https://github.com/martaxi-boss/VPS/actions/runs/42513141634): **PASS** após importação → corte → gravação → exportação → verificação independente.

## Critério de classificação honesto

**OpenShot demonstrou um fluxo funcional real controlável por CLI, e não apenas a abertura da AppImage.** O ensaio não certifica a totalidade dos efeitos, todos os codecs, integração com GPU, uma GUI interativa, sessões longas, projetos reais de clientes ou exportações de alta resolução. Também **não** criou uma nova ação tipada ou operação base no catálogo universal; a classificação permanece **173 programas, 280 funções e 458 entradas** (51 programas diretamente acionáveis, 18 de suporte/opcionais sem operação direta). Não inflacionar estes números até existir uma interface admitida ao motor com entrada/saída e regressões próprias.

**Arquitetura:** IA anfitriã partilhada → Ruflo temporário → papéis → único motor Ferrari/catálogo. Não exigir agentes LLM autónomos.
