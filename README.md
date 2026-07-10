# 🚀 Parametrização N2

Central interna para documentação técnica, scripts SQL, correções N2, DataSync e ferramentas de apoio à equipe de suporte.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-blue)
![License](https://img.shields.io/badge/license-Private-red)

---

# 📖 Sobre o projeto

O **Parametrização N2** é uma plataforma web desenvolvida para centralizar todas as documentações técnicas da equipe N2 da Softcom.

O objetivo é eliminar consultas espalhadas em arquivos, facilitar o compartilhamento de conhecimento e disponibilizar ferramentas utilizadas diariamente pela equipe.

Hoje o sistema possui uma interface moderna, responsiva e compatível com tema claro e escuro.

---

# ✨ Funcionalidades

## 📊 Dashboard

- Métricas em tempo real
- Quantidade de Scripts
- Quantidade de Correções
- Downloads DataSync
- Últimos Scripts
- Últimas Correções
- Gráficos de utilização
- Cards animados

---

## 💻 Scripts SQL

- Cadastro de Scripts
- Editor SQL (CodeMirror)
- Destaque de Sintaxe
- Formatação automática
- Copiar SQL
- Tela de visualização
- Pesquisa
- Filtros
- Contagem de acessos
- Estatísticas
- Dashboard interno

---

## 🔧 Correções N2

- Cadastro de Correções
- Classificação por criticidade
- Categorias
- Editor SQL
- Pesquisa
- Histórico
- Métricas
- Contagem de acessos
- Dashboard interno

---

## ☁️ DataSync

Cadastro de ferramentas utilizadas pelo suporte.

Cada ferramenta possui:

- Nome
- Tipo
- Link para Download
- Contador de Downloads

O download é realizado através de links externos evitando o limite de upload da Vercel.

---

## 🆔 Gerador de Identificador

Ferramenta para geração rápida de identificadores.

Possui:

- Histórico
- Exportação TXT
- Copiar Número
- Copiar Identificador
- Copiar Tudo
- Atalho CTRL + ENTER
- Histórico Local
- Contadores

---

# 🖥️ Interface

O sistema possui:

- Tema Claro
- Tema Escuro
- Sidebar Responsiva
- Breadcrumb
- Cards Modernos
- Dashboard
- Sparkline Charts
- Layout Responsivo

---

# 🛠️ Tecnologias

Backend

- Python
- Flask
- SQLAlchemy
- Psycopg
- PostgreSQL

Frontend

- Bootstrap 5
- Bootstrap Icons
- Chart.js
- CodeMirror
- JavaScript
- HTML5
- CSS3

Banco

- PostgreSQL (Neon)

Hospedagem

- Vercel

---

# 📂 Estrutura

```
app.py

models.py

templates/
│
├── dashboard.html
├── scripts/
├── correcoes/
├── datasync/
└── conversao/

static/
│
├── css/
├── js/
└── img/

instance/

requirements.txt
README.md
```

---

# ⚙️ Instalação

Clone o projeto

```bash
git clone https://github.com/Danyebert/parametrizacao_n2_scripts2.0.git
```

Entre na pasta

```bash
cd parametrizacao_n2_scripts2.0
```

Crie o ambiente virtual

Windows

```bash
python -m venv .venv
```

Linux

```bash
python3 -m venv .venv
```

Ative

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

Instale

```bash
pip install -r requirements.txt
```

---

# ▶️ Executar

```bash
python app.py
```

ou

```bash
flask run
```

---

# 🌐 Deploy

Projeto preparado para deploy na:

- Vercel

Banco:

- PostgreSQL Neon

---

# 🔐 Variáveis de Ambiente

```env
DATABASE_URL=

SECRET_KEY=
```

---

## Próximas versões

- Controle de usuários
- Favoritos
- Pesquisa Global
- Logs de Auditoria
- Dashboard Administrativo
- Notificações
- API REST

---

# 👨‍💻 Desenvolvedor

**Danyebert Pereira**

LinkedIn

www.linkedin.com/in/danyebert-pereira-452a69136

GitHub

https://github.com/Danyebert

---

# 📄 Licença

Projeto privado.

Uso interno da Softcom.

Todos os direitos reservados.