# Motor Ferrari — execução própria no Ubuntu

A inteligência artificial interpreta e organiza; os executores vivem no Motor Ferrari, independente de ChatGPT, Codex e dos seus programas. Existe apenas uma Skill de entrada, partilhável entre anfitriões que consigam executar os seus comandos via CLI ou MCP autenticado.

## Estado

- **125 projetos públicos GitHub** curados por metadados a 02/11/2026, em `engine/ferrari_registry.json` (50) e `engine/ferrari_expansion.json` (75). O catálogo antigo contém 69 entradas com sobreposição. Nenhuma destas contagens equivale a ferramentas instaladas.
- O motor detecta binários, classifica pedidos, sugere ferramentas e disponibiliza sete operações reais e tipadas.
- Ferramenta catalogada não é instalada; binário encontrado não implica execução certificada.
- Ubuntu da VPS, recursos, REA, Ruflo, integridade dos downloads e ligação a IA ainda têm de ser verificados no anfitrião real.

## Diagnóstico, seleção e testes

    python3 -m engine.ferrari doctor
    python3 -m engine.ferrari list --category reverse
    python3 -m engine.ferrari plan 'Criar um site profissional'
    python3 -m engine.ferrari packages --profile maximum
    python3 -m unittest discover -s tests -v

## Operações implementadas

    python3 -m engine.ferrari run --operation web-template --title 'A minha loja' --output /tmp/website
    python3 -m engine.ferrari run --operation svg-poster --title 'Campanha' --output /tmp/creative
    python3 -m engine.ferrari run --operation pdf-text --input /tmp/doc.pdf --output /tmp/pdf
    python3 -m engine.ferrari run --operation image-resize --input /tmp/foto.jpg --output /tmp/imagem
    python3 -m engine.ferrari run --operation video-thumbnail --input /tmp/video.mp4 --output /tmp/thumbnail
    python3 -m engine.ferrari run --operation apk-decompile --input /tmp/app.apk --output /tmp/apk
    python3 -m engine.ferrari run --operation binary-strings --input /tmp/programa.elf --output /tmp/bin

As duas primeiras são templates locais. As restantes exigem executores instalados (pdftotext, ImageMagick, FFmpeg, JADX, strings). A operação JADX não é REA completo.

## Instalação Ubuntu 24.04+

    bash install/ferrari-ubuntu.sh --profile maximum
    bash install/ferrari-ubuntu.sh --profile maximum --headless
    sudo bash install/ferrari-ubuntu.sh --profile maximum --apply

O instalador é simulação por defeito. O modo --apply só instala pacotes dos repositórios APT Ubuntu configurados. Programas externos como REA, Ghidra, JADX, Ruflo e ComfyUI exigem instalação independente com versão, licença, integridade e testes. Sem PPAs automáticos, instalações clandestinas ou alterações a outros projetos.

## Conjunto recomendado

| Área | Componentes |
|---|---|
| Web | Next.js, Astro, Vite, Tailwind, shadcn/ui, Bootstrap, Playwright |
| Engenharia reversa | REA, Ghidra, JADX, Apktool, radare2, Rizin, Binwalk, angr, MobSF |
| Criativos | GIMP, Krita, Blender, Inkscape, ImageMagick, libvips |
| Multimédia | FFmpeg, Kdenlive, faster-whisper |
| Documentos | LibreOffice, Pandoc, OCRmyPDF, Tesseract, Scribus, Typst |
| Orquestração | Ruflo, LangGraph, MCP, Ansible |
| IA visual | ComfyUI, InvokeAI, normalmente exigem GPU |

Licenças comerciais não ficam desbloqueadas. Para funções Adobe, usar alternativas livres legais. Estrelas GitHub medem popularidade, não funcionamento Ubuntu.

## Para certificar o motor

Verificar a VPS real, instalar o perfil máximo APT, incorporar ferramentas upstream compatíveis, certificar executores com ficheiros reais e configurar acesso autenticado da Skill até ao motor. Só assim pode ser atribuída uma percentagem séria de cobertura.

## Descoberta automática de repositórios gratuitos

O Ferrari pode procurar **repositórios GitHub públicos** através da API REST gratuita, sem instalar o código encontrado. Classifica candidatos por estrelas, exclui forks/arquivados e exige uma licença livre identificada. Os repositórios encontrados devem passar ainda por verificação de licença no upstream, suporte efetivo Ubuntu, dependências, arquitetura e testes.

```bash
python3 -m engine.ferrari discover "linux open source vector design" --min-stars 100 --limit 15
python3 -m engine.ferrari alternatives "Adobe Photoshop"
python3 -m engine.ferrari alternatives "AutoCAD"
```

Os 18 mapeamentos em `engine/commercial_alternatives.json` relacionam aplicações comerciais com **alternativas independentes legítimas**, nunca cracks, binários adulterados, licenças contornadas ou fornecedores pagos tornados gratuitos artificialmente. Implementações livres de formatos e protocolos podem ser úteis, mas não concedem direitos de utilização do software original.

### Instalação e descoberta são operações diferentes

- **Catálogo GitHub:** metadados verificados, sem provas de Ubuntu ou execução.
- **Ferramenta APT:** proposta pelo instalador e só instalada com `--apply`; os pacotes APT da expansão continuam sem certificação e são excluídos da instalação automática.
- **Ferramenta em execução:** precisa de binário verificado, testes de entrada/saída e integração MCP/CLI reais.
- **Interface gráfica:** numa VPS sem display é preciso processamento headless válido ou sessão gráfica dedicada.
- **IA local e difusão:** modelos, pesos e GPU podem não caber na VPS; um projeto open-source não implica GPU grátis ou API sem quotas.

O motor continua a precisar de adaptadores por ferramenta; uma entrada no catálogo não é uma capacidade de execução automática.
