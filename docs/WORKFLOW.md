# Fluxo de uso

## Projeto

1. Instale os templates em uma pasta Codex escolhida; se houver diferenças, faça integração manual.
2. No repositório de trabalho, mantenha AGENTS.md com comandos e regras específicos do projeto.
3. Para novos comportamentos, defina prova de aceitação e testes que alcancem a mudança.
4. Rode os gates locais e registre resultados; confira interface e mecanismo real quando aplicável.
5. Use revisão independente disponível. Não presuma que um agente de outro produto exista neste ambiente.

## Publicação desta base

1. Atualize arquivos públicos e manifesto. Rode `python scripts/test.py`.
2. Exporte para pasta nova e revise o conteúdo, incluindo nomes de arquivos e metadados Git.
3. Publique em repositório de histórico novo, com identidade pública/noreply nos commits.
4. Abra PR com comandos, resultados, limites e revisão. Não envie relatórios privados no corpo do PR.
5. Antes do merge, atualize a branch com a principal e repita o gate no SHA que será integrado.
6. Faça squash com `gh pr merge --squash --match-head-commit <sha-validado>` quando autorizado e todos os gates passarem.

Sandbox restringe ferramentas e acessos. AGENTS orienta decisões; não é um firewall.
As opções de rede do workspace controlam o shell nesse sandbox; não desabilitam automaticamente MCP, apps ou web.
