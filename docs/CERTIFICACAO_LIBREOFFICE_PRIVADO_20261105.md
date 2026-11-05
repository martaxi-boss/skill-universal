# Certificação manual — LibreOffice privado no Ferrari (05/11/2026)

**Fonte:** captura de ecrã do utilizador no ConnectBot, VPS Ubuntu, 05/11/2026 às 15:22 UTC. A captura é evidência da execução observada, não de auditoria independente posterior aos ficheiros ou dependências carregadas.

## Resultado observado

- `FERRARI_PRIVATE_OFFICE_LOCAL_COPY=PASS`
- `FERRARI_PRIVATE_OFFICE_VERSION=LibreOffice 24.2.7.2 420(Build:2)`
- Conversão real, com mensagem `convert ... demo.docx as a Writer document -> ... demo.pdf using filter : writer_pdf_Export`
- `FERRARI_PRIVATE_OFFICE_PDF_TEST=PASS`
- `FERRARI_PRIVATE_OFFICE_INSTALL=PASS`

O instalador `install/vps-private-office.sh` foi executado diretamente como utilizador não-root, copiando ficheiros do LibreOffice Ubuntu preexistente (somente leitura) para `/srv/projects/skill-universal/tools/libreoffice/`, ajustando os caminhos internos da cópia e executando a conversão num workspace temporário em `.runtime/`. O script não executa APT, não atualiza o Ubuntu, não reinicia serviços e apaga o seu workspace temporário no final.

## Aviso e limites

A saída contém `Warning: failed to launch javaldx - java may not function correctly`. O aviso **não impediu a conversão DOCX→PDF**, mas a integração Java e tarefas que requerem Java *não* foram certificadas. A verificação de assinatura do pacote base Ubuntu e a auditoria exaustiva de bibliotecas dinâmicas que o LibreOffice carrega não foram efetuadas por esta prova.

**Por comprovar:** a nova versão do motor em `current`, execução `office-pdf` pela Skill→GitHub Actions→VPS→ZIP, inventário físico de todos os outros executáveis e dependências globais, e possibilidade de desinstalar o Ferrari sem efeitos noutros projetos. Não remover a instalação Ubuntu original de LibreOffice até verificar consumidores alheios.

O CAD/Blender privado já tinha sido certificado separadamente em [CAD_PRIVADO_TESTE_MANUAL_20261105.md](CAD_PRIVADO_TESTE_MANUAL_20261105.md).

**Porta da próxima fase:** inspecionar e instalar uma nova release versionada apenas dentro do projeto, testar todas as ações em produção com capacidade privada, verificar fallback e só depois proceder a limpeza exclusivamente Ferrari. Sem novos serviços, coordenadores ou alterações SSH.
