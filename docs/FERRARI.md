# Motor Ferrari — execução própria no Ubuntu

A inteligência artificial interpreta e organiza; os executores vivem no Motor Ferrari, independente de ChatGPT, Codex e dos seus programas. Existe apenas uma Skill de entrada, partilhável entre anfitriões que consigam executar os seus comandos via CLI ou MCP autenticado.

## Estado

- 50 projetos GitHub verificados por metadados a 02/11/2026, em engine/ferrari_registry.json, complementam o catálogo original de 69 entradas, com sobreposição. Não representam 119 ferramentas instaladas.
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
