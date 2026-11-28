# Seleção para a base universal

Comparação em 2026-10-22. Fontes: diretrizes e scripts das configurações Codex e Claude Code;
inventário e nomes de opções globais, sem copiar credenciais nem estado de execução.

| Tema | Decisão para Codex | Motivo |
| --- | --- | --- |
| Diretrizes dos dois produtos | Consolidar e reescrever | Grande parte era duplicada; juntar aumentaria contexto sem ganho |
| Estilo e execução | Português curto, autonomia, objetivo verificável e ponto de virada | Reutilizável sem perfil pessoal |
| Qualidade | Testes reais, sintaxe, links, conflitos e regressões de segurança | Aproveita a disciplina dos dois conjuntos |
| Scanner | Gitleaks obrigatório, saída omitida e varredura de histórico quando existir | Ausência do scanner não pode resultar em sucesso |
| Git | Branch, isolamento, revisão e merge pelo SHA validado | Preserva trabalho concorrente e vincula prova ao conteúdo |
| Permissões | Aprovação sob demanda, workspace e rede restrita | Segurança executável além das instruções |
| Modelo e esforço | Sem modelo ou plano fixo | Disponibilidade, custo e tarefa variam |
| MCP e plugins | Configuração local opcional | Evita credenciais, dependências e serviços obrigatórios |
| Agentes | Usar somente tipos realmente disponíveis e autorizados | Nomes e protocolos do Claude não são portáveis para o Codex |
| Hooks Claude | Não portar diretamente | Eventos e ferramentas diferem; texto não substitui mecanismo testado |
| Perfil pessoal | Excluir carreira, aprendizado, nomes, caminhos e histórico | Não pertence a uma base universal pública |
| Histórico Git das fontes | Preservar privado e iniciar outro histórico | Apagar arquivos do último commit não remove versões anteriores |

Foram reescritas práticas gerais. Não foram copiados código de plugins, skills de terceiros ou hooks das fontes.
Os relatórios privados foram identificados pelo inventário; não são necessários para esta entrega.

## Limites da prova

- Defaults conferidos na documentação oficial e analisados como TOML; não foi iniciada sessão de inferência.
- Instalação, preservação e exportação testadas no filesystem real, em pastas temporárias.
- Scanner cobre padrões e segredos reconhecíveis; revisão humana continua necessária para dados pessoais em prosa.
- A verificação deste pacote não representa auditoria completa das configurações privadas de origem.
