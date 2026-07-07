# Instalação no Vercel

## 1. Criar banco PostgreSQL

Use Neon ou Supabase.

Copie a connection string PostgreSQL. Exemplo:

```txt
postgresql://usuario:senha@host:5432/banco?sslmode=require
```

## 2. Enviar projeto para GitHub

```bash
git init
git add .
git commit -m "primeira versao parametrizacao n2"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/parametrizacao-n2-scripts.git
git push -u origin main
```

## 3. Importar no Vercel

1. Acesse o Vercel.
2. Clique em **Add New Project**.
3. Selecione o repositório do GitHub.
4. Framework: **Other**.
5. Mantenha o build padrão do Vercel.

O arquivo `vercel.json` já aponta para `api/index.py`.

## 4. Configurar variáveis de ambiente

Em **Settings > Environment Variables**, adicione:

```txt
DATABASE_URL=postgresql://usuario:senha@host:5432/banco?sslmode=require
SECRET_KEY=uma-chave-grande-e-segura
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASSWORD=admin123
```

Depois clique em **Redeploy**.

## 5. Primeiro acesso

Acesse a URL gerada pelo Vercel.

Login inicial:

```txt
Usuário: admin
Senha: admin123
```

Depois vá em **Alterar senha**.

## 6. Banco de dados

O app cria as tabelas automaticamente com `db.create_all()` na inicialização.

Também existe o arquivo `schema.sql` caso você queira criar manualmente no Neon/Supabase SQL Editor.

## Observações importantes para Vercel

- Vercel não é ideal para persistir arquivos no disco.
- Os uploads de imagens das correções já são salvos no PostgreSQL.
- Os uploads de DataSync/conversão também podem ser salvos no PostgreSQL pela tela administrativa.
- Para arquivos muito grandes, use Supabase Storage, S3, Google Drive ou outro storage externo.
