# Manutenção da configuração pública

Leia [docs/DECISIONS.md](docs/DECISIONS.md) antes de alterar a arquitetura.

- Este repositório contém apenas material público escrito do zero. Fontes privadas ficam fora do Git e da exportação.
- A regra global instalável está em templates/AGENTS.md. Este arquivo orienta apenas manutenção do pacote.
- Rode `python scripts/test.py` antes de publicar. Precisa de Python 3.12+, Git e Gitleaks.
- Declare cada novo arquivo em public-manifest.json. Verificação bloqueia arquivos extras, links e padrões pessoais.
- Modifique o instalador junto com testes reais de preservação, repetição e exportação.
- Preserve os limites de aprovação e sandbox. Configuração universal não inclui modelo fixo, conta, MCP ou confiança local.
- Não sincronize automaticamente este pacote com a configuração global instalada de uma pessoa.
- Use branch, PR e revisão independente. Revisor obrigatório indisponível: deixe o PR aberto.
