# Parametrização N2 Scripts

Sistema web interno para centralizar documentação técnica da equipe N2: correções, scripts SQL, bancos mapeados, downloads do DataSync, ferramentas de conversão e gerador de identificador.

## Tecnologias

- Python Flask
- PostgreSQL, compatível com Neon e Supabase
- SQLAlchemy
- Bootstrap 5
- Bootstrap Icons
- Jinja2
- JavaScript
- CodeMirror
- Deploy compatível com Vercel

## Funcionalidades

### Autenticação

- Usuário visitante visualiza dados.
- Usuário administrador cria, edita, exclui, importa e exporta.
- Admin padrão criado automaticamente caso não exista:
  - usuário: `admin`
  - senha: `admin123`
- Altere a senha após o primeiro login.

### Correções N2

- CRUD completo.
- Busca por texto.
- Filtros por categoria e criticidade.
- Campos técnicos com CodeMirror.
- Upload múltiplo de imagens JPG, JPEG e PNG salvo no banco.
- Remoção lógica de correções e anexos.
- Exportação JSON.
- Importação JSON no formato atual e legado.

### Scripts SQL

- CRUD completo.
- Cadastro de script com múltiplas consultas vinculadas.
- Editor SQL com CodeMirror.
- Botão copiar por consulta.
- Botão copiar todos.

### Banco de Dados Mapeados

- Cadastro simples de bancos mapeados, tipo, descrição e observações.

### DataSync e Ferramentas de Conversão

- Lista arquivos/pastas locais em `local_files/datasync` e `local_files/conversao`.
- Baixa arquivo direto.
- Compacta pasta em ZIP quando necessário.
- Se a pasta tiver apenas um `.zip`, `.rar` ou `.7z`, baixa o arquivo direto.
- Upload de arquivos para PostgreSQL pelo usuário administrador.
- Contador de downloads para arquivos armazenados no banco.

> Observação: no Vercel o sistema de arquivos é efêmero. Para produção, use a função de upload para banco ou um storage externo.

### Gerador de Identificador

Entrada de exemplo:

```txt
05/26 - 72051 - SILVANIO DIREÇÕES HIDRAULICAS - ARAPIRACA
```

Resultado:

- número: `72051`
- identificador: `silvaniodirecoeshidraulicasarapiraca`

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

No Linux/WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
source .venv/bin/activate
flask --app app.py run --host=0.0.0.0 --port=5000 --debug --no-reload
python app.py
```

Acesse: `http://127.0.0.1:5000`
