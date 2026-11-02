# Guia de execução da Skill

## ChatGPT

Uma Skill local contém instruções, não credenciais. Para utilizar o motor na VPS deve existir um conector com ferramentas motor_* ou outro canal autenticado, capaz de transportar ficheiros e resultados. O presente ZIP não configura essa ligação. Sem ela, executar somente o que o ChatGPT permite nativamente e documentar o limite.

## Codex e clientes MCP

No checkout isolado do motor, iniciar `python3 -m integrations.mcp_server` num Python virtualenv que tenha o SDK MCP. Fazer a ligação ao cliente por `stdio` segundo as suas instruções oficiais. Os programas do sistema não devem ser instalados no checkout de outros projetos.

## Diferenças entre níveis

1. Catalogado: a ferramenta está na lista, nada mais.
2. Instalável: dependências e repositórios confirmados naquele host.
3. Instalado: existe um binário detectável.
4. Funcional: passou um teste real com dados conhecidos.
5. Disponível ao cliente: a ponte e autenticação foram testadas de ponta a ponta.

Não usar 'pronto a 100%' se o nível 5 estiver por certificar. Nunca usar ferramentas pagas como substituição automática.

## Critérios de escolha

Compatibilidade Linux/arquitetura; licenciamento livre/gratuito; disponibilidade real; adequação ao formato; qualidade; requisitos de CPU/RAM/disco; privacidade de ficheiros; evidência de testes. O custo de uma chamada de API deve ser verificado no momento, não presumido com base em documentação antiga.

## Exemplos

- 'Faz um site profissional de um restaurante' -> `motor_plan` -> template web local, ou criar aplicação completa com ferramenta real se disponível -> ficheiros e testes.
- 'Cria um criativo para um produto' -> procurar geração de imagem do anfitrião; sem esse executor, criar SVG/composição e esclarecer a diferença.
- 'Analisa este APK' -> ficheiro real -> identificação + hash -> REA/JADX/Apktool se realmente instalados e configurados -> relatório fundamentado.
