# Deploy no Azure Static Web Apps

Estas instruções mostram duas formas de criar e ligar o seu repositório GitHub ao Azure Static Web Apps.

Resumo recomendado
- Origem: **GitHub (autorizar)** — escolha e autorize a conta `mgoncalves86` no Portal.
- Repositório: selecione `chess2all-website` e a branch `main`.
- App location: `src`
- API location: deixe em branco
- Output location: deixe em branco

Opção A — Usar o Portal (mais simples)
1. No Azure Portal, crie um recurso **Static Web App**.
2. Em "Source", escolha **GitHub**, autorize `mgoncalves86` e selecione o repositório e a branch `main`.
3. Defina `App location` → `src`, `API location` → (vazio), `Output location` → (vazio).
4. Conclua a criação. O Portal normalmente cria um workflow GitHub Actions e adiciona um Secret no repositório (ex.: `AZURE_STATIC_WEB_APPS_API_TOKEN_...`).
5. Verifique em GitHub: `Settings -> Secrets and variables -> Actions` para confirmar que o token existe.

Opção B — Criar via CLI e definir secret manualmente
1. Autentique no Azure e crie um grupo (opcional):
```bash
az login
az group create -n myResourceGroup -l "West US"
```
2. Criar o Static Web App (substitua nomes):
```bash
az staticwebapp create -n myStaticApp -g myResourceGroup \
  --source https://github.com/mgoncalves86/chess2all-website --branch main \
  --location "West US" --app-location "src" --output-location ""
```
3. Se precisar de um token manual (deployment token):
   - No recurso Static Web App no Portal abra **Manage deployment token** e copie o token.
   - No GitHub, adicione um Secret (repo): `AZURE_STATIC_WEB_APPS_API_TOKEN` com esse token.
   - Ou use `gh`:
```bash
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "<TOKEN>" --repo mgoncalves86/chess2all-website
```

Observações importantes
- Workflow: já existe um arquivo criado automaticamente pelo Portal em `.github/workflows/` apontando para `src` — mantenha esse arquivo único para evitar conflitos.
- Se preferir usar um workflow personalizado, garanta que o Secret do Azure está presente com o nome utilizado pelo workflow.

Sobre `forms/contact.php`
- `Azure Static Web Apps` não executa PHP. Se o formulário do site usa `forms/contact.php`, escolha uma das opções:
  1. Converter `contact.php` para uma Azure Function (HTTP-trigger, Node/Python/C#) e colocá-la em `api/` no repo.
  2. Usar um serviço de terceiros para formulários (Formspree, Getform, etc.) e alterar o `action` do formulário para o endpoint do serviço.
  3. Hospedar a parte do formulário num App Service (PHP) separado — solução mais complexa.

Verificação final
- Push para `main` deverá acionar o workflow e publicar o site no domínio provisório do Static Web Apps.
- Se quiser, eu posso adicionar um `api/` de exemplo (Node) para substituir `contact.php`.

--
Arquivo criado automaticamente por assistência para deploy.
