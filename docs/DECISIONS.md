# Decisões

## 2026-10-22 — Público e privado independentes

Manter repositório, pasta e histórico públicos independentes das fontes privadas.
Por quê: históricos de Git preservam arquivos removidos, incluindo relatórios e identificadores de sessões.
Inicialização remota deve ser vazia; commits locais usam identidade pública noreply, verificada automaticamente.
Por quê: README criado pelo GitHub pode usar e-mail pessoal nos metadados mesmo com conteúdo público.

## 2026-10-22 — Lista explícita e bloqueio na dúvida

Manifesto exato, padrões de privacidade e Gitleaks obrigatório antes de instalar ou exportar.
Por quê: `.gitignore` sozinho não impede publicar arquivos já rastreados ou novos documentos pessoais.
O scanner complementa a revisão; não promete reconhecer toda informação pessoal em linguagem natural.

## 2026-10-22 — Configuração mínima e regras independentes

Separar AGENTS de manutenção do template global. Manter somente aprovação, sandbox e restrição de rede no TOML.
Por quê: caminhos, modelos, preferências, confiança de projetos e integrações variam por máquina e conta.
Não usar imports `@arquivo` específicos de outro agente como se fossem carregamento automático do Codex.

## 2026-10-22 — Biblioteca padrão e instalação conservadora

Python 3.12+ com tomllib e unittest; PowerShell é só um atalho opcional. Nenhuma dependência Python externa.
Por quê: resolve validação TOML e testes portáveis com custo de manutenção baixo; já existe runtime local.
Instalador não substitui arquivos diferentes e exige destino explícito, preservando personalização e dados.
O mínimo 3.12 garante detecção nativa de junctions do Windows, inclusive nos arquivos de destino.

## 2026-10-22 — Sem alteração global implícita

Não instalar esta base automaticamente sobre regras privadas existentes.
Por quê: publicação e troca da configuração em uso são ações distintas; regras pessoais não devem sumir no processo.
