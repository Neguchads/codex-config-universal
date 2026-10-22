# Segurança e privacidade

- Apenas arquivos do manifesto entram na exportação. Nunca reutilize histórico Git das fontes privadas.
- Não publique configurações globais brutas, auth, variáveis de ambiente, sessões, memórias, bancos ou logs.
- Padrões de caminhos locais, e-mails, rede privada, identificadores de sessão e chaves privadas bloqueiam o gate.
- Gitleaks é obrigatório para arquivos e histórico Git existente. A saída dos achados não é reproduzida.
- E-mails de autor e committer em todas as referências locais devem usar domínio público noreply do GitHub.
- Crie o repositório remoto vazio; README automático pode usar a identidade pessoal configurada na conta.
- Revisão humana deve procurar nomes, contexto pessoal e dados não reconhecíveis por padrões.
- Arquivos extras bloqueiam o gate mesmo quando ignorados pelo Git; apenas `.git`, caches Python e `dist` são
  excluídos da auditoria de árvore. Esses diretórios nunca entram na exportação pelo manifesto.
- O instalador preserva arquivos diferentes. Faça backup privado antes de qualquer integração manual.
- Não há telemetria nem serviço externo nos scripts. Gitleaks e Git são executados localmente.
- Não envie vulnerabilidades com valores reais em issues. Use o canal privado de segurança do GitHub, quando
  habilitado; caso contrário, comunique apenas uma descrição sem dados sensíveis.
- Segredo publicado é comprometido: revogue/rotacione primeiro; trate depois arquivos e histórico com autorização.

Limites: não existe garantia absoluta de ausência de dados pessoais; manifesto, scanner e revisão são complementares.
Não foram auditados todos os históricos privados. Este pacote não instala hooks de segurança em outras ferramentas.
