# Codex Universal Config

Base pública para Codex CLI, IDE e aplicativo, derivada da comparação entre configurações Codex e Claude Code.
Regras reutilizáveis, configuração mínima e publicação por lista explícita de arquivos.

## O que entrega

- Orientações em português: autonomia com limites, menor solução completa, testes reais, revisão e Git seguro.
- Configuração com aprovação sob demanda, escrita limitada ao workspace e rede do shell desabilitada por padrão.
- Instalação que preserva arquivos existentes e bloqueia diferenças antes de escrever.
- Verificação local de sintaxe, links, conflitos, padrões pessoais, segredos e artefato exportado.

Nenhum modelo ou plano é obrigatório. Conta, modelos disponíveis, integrações, permissões administrativas e
preferências pessoais são configurados localmente. Políticas gerenciadas podem prevalecer sobre estes defaults.

## Requisitos e verificação

Python 3.12 ou superior, Git e Gitleaks 8.30.1 (versão validada; nenhuma biblioteca Python externa).
O gate completo também requer Codex CLI instalado para conferir o carregamento do TOML, sem inferência.
No Windows, instale Gitleaks pelo pacote `Gitleaks.Gitleaks` do winget ou por sua distribuição oficial.

```powershell
python scripts/test.py
# Atalho no Windows:
.\scripts\test.ps1
```

O gate falha se Gitleaks estiver ausente. Resultados do scanner são omitidos para evitar divulgar valores sensíveis.
Python usa apenas a biblioteca padrão. O lint local cobre sintaxe, manifesto, links e conflitos; não há compilação
de aplicação neste pacote. Os testes exercitam instalação e exportação reais em diretórios temporários.

## Instalação

Confira primeiro [templates/AGENTS.md](templates/AGENTS.md) e [templates/config.toml](templates/config.toml).

```powershell
python scripts/config.py install --target "$HOME/.codex"
```

Linux e macOS usam o mesmo comando Python; conforme a instalação, use `python3`.
Se você definiu `CODEX_HOME`, informe seu valor em `--target` em vez do caminho padrão.
O instalador cria apenas `AGENTS.md` e `config.toml`. Repetir com conteúdo igual é seguro.
Arquivos existentes diferentes fazem a operação parar antes da primeira escrita; compare e integre manualmente,
preservando sua cópia privada. Não existe opção de sobrescrever ou remover configuração.

`AGENTS.override.md` existente pode substituir a orientação global. Configuração de projeto, argumentos da CLI
e políticas gerenciadas também podem mudar o comportamento efetivo. Verifique-os na instalação real.
O pacote não configura sandbox específico do sistema nem declara que instruções textuais impedem ações perigosas.

## Exportação pública

```powershell
python scripts/config.py export --target ../codex-public-release
```

O destino deve ser novo e externo ao repositório. A exportação contém somente os arquivos de
[public-manifest.json](public-manifest.json), após o gate de privacidade e Gitleaks.
Nunca copie `.git` de uma configuração privada. A base pública deve ter histórico novo.

## Estrutura e escolhas

| Arquivo | Uso |
| --- | --- |
| [templates/AGENTS.md](templates/AGENTS.md) | Regras globais instaláveis, independentes de caminhos pessoais |
| [templates/config.toml](templates/config.toml) | Opções mínimas de segurança do Codex |
| [docs/ANALYSIS.md](docs/ANALYSIS.md) | Comparação, seleção e exclusões |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Decisões técnicas e seus motivos |
| [docs/WORKFLOW.md](docs/WORKFLOW.md) | Uso diário, revisão e publicação |
| [SECURITY.md](SECURITY.md) | Limites e procedimento de segurança |
| [ROADMAP.md](ROADMAP.md) | Estado e próximas validações |

Sem dependências de runtime externas, hooks importados, skills comerciais ou plugins obrigatórios.
Não há licença de redistribuição definida nesta versão; publicar o código não concede automaticamente uma licença.

Base documental: [configuração oficial do Codex](https://learn.chatgpt.com/docs/config-file/config-reference)
e [instruções AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
Validado localmente em Windows com Codex CLI 0.163.0-alpha.11; Linux, macOS, IDE, aplicativo e uso de modelo
em uma sessão nova ainda precisam de validação funcional. O pacote não faz chamadas pagas de modelo nos testes.
