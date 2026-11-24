# Fechamento operacional — GitHub

Escopo: os oito repositórios públicos originais da conta Neguchads; ComfyUI fica de fora. O script `scripts/finalize_github.py` é executado **localmente pelo administrador**, não por GitHub Actions. Não pede tokens em texto, não altera regras existentes e não usa bypass de proteção.

## 1. Pré-visualizar e aplicar

Com Python 3.10+ e GitHub CLI autenticado como Neguchads:

```powershell
gh auth status
python scripts/finalize_github.py
python scripts/finalize_github.py --apply-rulesets
```

O primeiro comando Python apenas lê o estado e mostra os JSONs; o segundo cria regras ativas, verificando os checks reais na branch padrão. As regras impedem pushes diretos, force-push e exclusão, exigem PR, squash merge, resolução de conversas e checks bem-sucedidos no código atualizado. Repositórios com proteção existente, permissões insuficientes ou checks ausentes são ignorados com erro, sem substituir configurações. Um administrador pode ajustar as regras posteriormente em Settings > Rules > Rulesets.

A política assume desenvolvimento individual: exige zero revisores humanos independentes, mas exige checks. Caso exista outro revisor, acrescente `--approvals 1`. Não use essa opção para um projeto individual sem revisor disponível.

## 2. Release planning

Nos repositórios starlight-bi e favorite-manager, permita criação de PRs por Actions em Settings > Actions > General (a opção também permite aprovação por Actions; avalie esse impacto). Depois:

```powershell
python scripts/finalize_github.py --enable-release-planning
gh workflow run version-proposal.yml --repo Neguchads/starlight-bi --ref main
gh workflow run version-proposal.yml --repo Neguchads/favorite-manager --ref main
```

A opção explícita acima grava somente a variável de habilitação. Release Please continua sem publicar GitHub Releases automaticamente. O script não altera a permissão administrativa de Actions. Se for necessário aprovar runs criados pelo bot, faça isso na interface do GitHub.

## 3. Evidências de supply chain

Os cinco repositórios com supply-chain.yml preservam o disparo manual. Rode a partir da branch padrão, por exemplo:

```powershell
gh workflow run supply-chain.yml --repo Neguchads/cdos-nintendods-recomp --ref main
gh run list --repo Neguchads/cdos-nintendods-recomp --workflow supply-chain.yml
```

Para Xbox, use `--ref publish/public-safe`. Baixe o artefato de uma execução bem-sucedida, valide o SHA-256 e use `gh attestation verify <arquivo> -R <owner/repo>`. Os três projetos de recompilação geram inventário de fonte, não um jogo executável. Atestação não comprova direitos autorais ou compatibilidade de saves.

## 4. Homologação local dos jogos

- Registrar commit e versões exatas de compilador, SDK, dependências e mídia original adquirida legitimamente.
- Compilar em ambiente Windows limpo; repetir sem alteração e registrar cache; alterar um arquivo original de teste, repetir e verificar invalidação seletiva.
- Validar pacote, checksums e manifesto; instalar em pasta separada dos dados do jogador.
- Usar cópia descartável de um save de versão anterior; testar carregamento, novo save, reinício, atualização e retorno à versão anterior. Registrar versão, hash anterior/posterior, resultado e logs sem dados pessoais.
- Verificar inicialização, controles, vídeo, áudio e encerramento; distinguir testes de smoke de playthrough.
- Não publicar ROM, BIOS, saves, mídia ou código gerado de terceiros sem direitos; não confundir testes sintéticos de runtime com execução real do jogo. Não publicar nenhum release antes de aprovar as evidências de autoria e licenciamento.

Referência: https://docs.github.com/en/rest/repos/rules
