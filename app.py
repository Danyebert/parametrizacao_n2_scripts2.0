import os, io, json, zipfile, unicodedata, re
from datetime import datetime
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func, text, case
from sqlalchemy.orm import load_only
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()

ALLOWED_IMAGES = {"jpg", "jpeg", "png"}
ARCHIVES = {".zip", ".rar", ".7z"}

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime)

class Usuario(db.Model, TimestampMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

class CorrecaoN2(db.Model, TimestampMixin):
    __tablename__ = "correcoes_n2"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    sistema = db.Column(db.String(150))
    categoria = db.Column(db.String(120))
    criticidade = db.Column(db.String(20), default="Baixa")
    erro = db.Column(db.Text)
    causa = db.Column(db.Text)
    correcao = db.Column(db.Text)
    acessos = db.Column(db.Integer, default=0, nullable=False)
    anexos = db.relationship("AnexoCorrecao", backref="correcao", lazy=True)

class AnexoCorrecao(db.Model, TimestampMixin):
    __tablename__ = "anexos_correcoes"
    id = db.Column(db.Integer, primary_key=True)
    correcao_id = db.Column(db.Integer, db.ForeignKey("correcoes_n2.id"), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.LargeBinary, nullable=False)

class CorrecaoAcesso(db.Model):
    __tablename__ = "correcoes_acessos"

    id = db.Column(db.Integer, primary_key=True)
    correcao_id = db.Column(db.Integer, db.ForeignKey("correcoes_n2.id"), nullable=False)
    data_acesso = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)
    quantidade = db.Column(db.Integer, default=1, nullable=False)

class ScriptSQL(db.Model, TimestampMixin):
    __tablename__ = "scripts_sql"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    tipo_banco = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    acessos = db.Column(db.Integer, default=0, nullable=False)
    consultas = db.relationship("ConsultaSQL", backref="script", lazy=True, cascade="all, delete-orphan")

class ScriptAcesso(db.Model):
    __tablename__ = "scripts_acessos"

    id = db.Column(db.Integer, primary_key=True)
    script_id = db.Column(db.Integer, db.ForeignKey("scripts_sql.id"), nullable=False)
    data_acesso = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)
    quantidade = db.Column(db.Integer, default=1, nullable=False)

class ConsultaSQL(db.Model, TimestampMixin):
    __tablename__ = "consultas_sql"
    id = db.Column(db.Integer, primary_key=True)
    script_id = db.Column(db.Integer, db.ForeignKey("scripts_sql.id"), nullable=False)
    titulo_consulta = db.Column(db.String(255), nullable=False)
    codigo_sql = db.Column(db.Text, nullable=False)
    ordem = db.Column(db.Integer, default=0)

class BancoMapeado(db.Model, TimestampMixin):
    __tablename__ = "bancos_mapeados"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(180), nullable=False)
    tipo_banco = db.Column(db.String(80))
    descricao = db.Column(db.Text)
    observacoes = db.Column(db.Text)

class ArquivoDownload(db.Model, TimestampMixin):
    __tablename__ = "arquivos_download"
    id = db.Column(db.Integer, primary_key=True)
    modulo = db.Column(db.String(30), nullable=False)  # datasync ou conversao
    nome = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(80), nullable=False)
    link_download = db.Column(db.Text)
    caminho = db.Column(db.String(500))
    conteudo = db.Column(db.LargeBinary)
    mime_type = db.Column(db.String(120))
    downloads = db.Column(db.Integer, default=0)

class ArquivoDownloadAcesso(db.Model):
    __tablename__ = "arquivos_download_acessos"

    id = db.Column(db.Integer, primary_key=True)
    arquivo_id = db.Column(db.Integer, db.ForeignKey("arquivos_download.id"), nullable=False)
    data_acesso = db.Column(db.Date, default=lambda: datetime.utcnow().date(), nullable=False)
    quantidade = db.Column(db.Integer, default=1, nullable=False)



def ensure_schema_updates():
    """Aplica pequenas alterações de schema que o db.create_all() não faz em tabelas existentes."""
    try:
        db.session.execute(text("ALTER TABLE scripts_sql ADD COLUMN IF NOT EXISTS acessos INTEGER DEFAULT 0 NOT NULL"))
        db.session.execute(text("ALTER TABLE correcoes_n2 ADD COLUMN IF NOT EXISTS acessos INTEGER DEFAULT 0 NOT NULL"))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS correcoes_acessos (
                id SERIAL PRIMARY KEY,
                correcao_id INTEGER NOT NULL REFERENCES correcoes_n2(id),
                data_acesso DATE NOT NULL DEFAULT CURRENT_DATE,
                quantidade INTEGER NOT NULL DEFAULT 1
            )
        """))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS scripts_acessos (
                id SERIAL PRIMARY KEY,
                script_id INTEGER NOT NULL REFERENCES scripts_sql(id),
                data_acesso DATE NOT NULL DEFAULT CURRENT_DATE,
                quantidade INTEGER NOT NULL DEFAULT 1
            )
        """))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS arquivos_download_acessos (
                id SERIAL PRIMARY KEY,
                arquivo_id INTEGER NOT NULL REFERENCES arquivos_download(id),
                data_acesso DATE NOT NULL DEFAULT CURRENT_DATE,
                quantidade INTEGER NOT NULL DEFAULT 1
            )
        """))
        db.session.commit()
    except Exception:
        db.session.rollback()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    db_url = os.getenv("DATABASE_URL", "sqlite:///local.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024

    # Evita reutilizar conexões PostgreSQL encerradas em instâncias serverless.
    if not db_url.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_recycle": 240,
            "pool_timeout": 20,
            "pool_size": 5,
            "max_overflow": 5,
            "connect_args": {
                "connect_timeout": 10,
                "application_name": "parametrizacao_n2",
            },
        }

    db.init_app(app)

    # Não execute db.create_all() ou ALTER TABLE em cada cold start da Vercel.
    # Para preparar/atualizar o banco, use o arquivo migrate.py entregue junto.
    if os.getenv("CREATE_DEFAULT_ADMIN", "false").lower() == "true":
        with app.app_context():
            create_default_admin()

    register_routes(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception is not None:
            db.session.rollback()
        db.session.remove()

    return app


def create_default_admin():
    nome = os.getenv("ADMIN_DEFAULT_USER", "admin")
    senha = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")
    if not Usuario.query.filter_by(nome=nome, deleted_at=None).first():
        db.session.add(Usuario(nome=nome, senha_hash=generate_password_hash(senha)))
        db.session.commit()


def is_admin():
    return bool(session.get("usuario_id"))


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_admin():
            flash("Faça login administrativo para executar esta ação.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGES


def normalize_identificador(texto):
    texto = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^a-zA-Z0-9]", "", texto)
    return texto.lower()



def extrair_dados_identificador(linha):
    """Extrai número e identificação de linhas com hífen, ponto e vírgula ou quebra de linha."""
    linha = (linha or "").strip()
    if not linha:
        return "", ""

    # Uniformiza os separadores mais comuns sem destruir textos internos.
    partes = [
        parte.strip()
        for parte in re.split(r"\s*(?:;|\r?\n|\s+-\s+)\s*", linha)
        if parte.strip()
    ]

    # Procura primeiro um bloco composto apenas por dígitos.
    numero = next((p for p in partes if re.fullmatch(r"\d+", p)), "")

    # Fallback para entrada sem separadores: ignora datas MM/AA e captura código numérico.
    if not numero:
        candidatos = re.findall(r"(?<![/\d])\d{3,}(?![/\d])", linha)
        numero = candidatos[0] if candidatos else ""

    partes_nome = []
    numero_consumido = False
    for parte in partes:
        if re.fullmatch(r"\d{1,2}/\d{2,4}", parte):
            continue
        if numero and parte == numero and not numero_consumido:
            numero_consumido = True
            continue
        partes_nome.append(parte)

    texto_nome = " ".join(partes_nome).strip()

    if not texto_nome:
        texto_nome = linha
        texto_nome = re.sub(r"\b\d{1,2}/\d{2,4}\b", " ", texto_nome)
        if numero:
            texto_nome = re.sub(rf"(?<!\d){re.escape(numero)}(?!\d)", " ", texto_nome, count=1)

    identificador = normalize_identificador(texto_nome)
    return numero, identificador


def get_file_listing(modulo):
    return ArquivoDownload.query.filter_by(
        modulo=modulo,
        deleted_at=None
    ).order_by(ArquivoDownload.nome).all()




def register_routes(app):
    @app.context_processor
    def inject_globals():
        return {"is_admin": is_admin(),
                "APP_VERSION": "2.7.6",
                "APP_BUILD": "2026-07-14",
                "APP_COPYRIGHT": "© 2026 Parametrização N2"}

    @app.route("/")
    def dashboard():
        try:
            dias = max(1, min(int(request.args.get("dias", 7)), 90))
        except (TypeError, ValueError):
            dias = 7

        resumo = db.session.query(
            db.session.query(func.count(CorrecaoN2.id))
            .filter(CorrecaoN2.deleted_at.is_(None))
            .scalar_subquery(),
            db.session.query(func.count(ScriptSQL.id))
            .filter(ScriptSQL.deleted_at.is_(None))
            .scalar_subquery(),
            db.session.query(func.count(ArquivoDownload.id))
            .filter(ArquivoDownload.deleted_at.is_(None))
            .scalar_subquery(),
            db.session.query(func.coalesce(func.sum(ArquivoDownload.downloads), 0))
            .filter(ArquivoDownload.deleted_at.is_(None))
            .scalar_subquery(),
        ).first()

        ultimas_correcoes = (
            CorrecaoN2.query
            .options(
                load_only(
                    CorrecaoN2.id,
                    CorrecaoN2.titulo,
                    CorrecaoN2.criticidade,
                    CorrecaoN2.updated_at
                )
            )
            .filter(CorrecaoN2.deleted_at.is_(None))
            .order_by(CorrecaoN2.updated_at.desc())
            .limit(5)
            .all()
        )

        ultimos_scripts = (
            ScriptSQL.query
            .options(
                load_only(
                    ScriptSQL.id,
                    ScriptSQL.titulo,
                    ScriptSQL.tipo_banco,
                    ScriptSQL.updated_at
                )
            )
            .filter(ScriptSQL.deleted_at.is_(None))
            .order_by(ScriptSQL.updated_at.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "dashboard.html",
            correcoes=int(resumo[0] or 0),
            scripts=int(resumo[1] or 0),
            bancos=0,
            downloads=int(resumo[2] or 0),
            total_downloads=int(resumo[3] or 0),
            dias=dias,
            ultimas_correcoes=ultimas_correcoes,
            ultimos_scripts=ultimos_scripts,
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = Usuario.query.filter_by(nome=request.form.get("nome"), deleted_at=None).first()
            if user and check_password_hash(user.senha_hash, request.form.get("senha", "")):
                session["usuario_id"] = user.id; session["usuario_nome"] = user.nome
                flash("Login realizado com sucesso.", "success")
                return redirect(url_for("dashboard"))
            flash("Usuário ou senha inválidos.", "danger")
        return render_template("auth/login.html")

    @app.route("/logout")
    def logout():
        session.clear(); flash("Sessão encerrada.", "info")
        return redirect(url_for("dashboard"))

    @app.route("/alterar-senha", methods=["GET", "POST"])
    @admin_required
    def alterar_senha():
        user = Usuario.query.get_or_404(session["usuario_id"])
        if request.method == "POST":
            if not check_password_hash(user.senha_hash, request.form.get("senha_atual", "")):
                flash("Senha atual inválida.", "danger")
            elif request.form.get("nova_senha") != request.form.get("confirmar_senha"):
                flash("Confirmação de senha não confere.", "danger")
            else:
                user.senha_hash = generate_password_hash(request.form.get("nova_senha")); db.session.commit()
                flash("Senha alterada com sucesso.", "success")
                return redirect(url_for("dashboard"))
        return render_template("auth/alterar_senha.html")

    @app.route("/correcoes")
    def correcoes_listar():
        busca = (request.args.get("busca") or "").strip()
        categoria = (request.args.get("categoria") or "").strip()
        criticidade = (request.args.get("criticidade") or "").strip()
        ordem = (request.args.get("ordem") or "recentes").strip()

        pagina = request.args.get("pagina", 1, type=int)
        por_pagina = request.args.get("por_pagina", 12, type=int)
        pagina = max(pagina or 1, 1)
        por_pagina = min(max(por_pagina or 12, 6), 48)

        base_filter = CorrecaoN2.deleted_at.is_(None)

        resumo = db.session.query(
            func.count(CorrecaoN2.id),
            func.sum(case((CorrecaoN2.criticidade == "Alta", 1), else_=0)),
            func.count(func.distinct(CorrecaoN2.categoria)),
            func.coalesce(func.sum(CorrecaoN2.acessos), 0),
        ).filter(base_filter).first()

        total_correcoes = int(resumo[0] or 0)
        alta_count = int(resumo[1] or 0)
        total_categorias = int(resumo[2] or 0)
        total_acessos = int(resumo[3] or 0)

        categoria_rows = db.session.query(
            CorrecaoN2.categoria,
            func.count(CorrecaoN2.id),
        ).filter(
            base_filter,
            CorrecaoN2.categoria.isnot(None),
        ).group_by(CorrecaoN2.categoria).order_by(CorrecaoN2.categoria).all()

        categorias = [nome for nome, _ in categoria_rows]
        distribuicao_categorias = [
            {"nome": nome, "qtd": qtd, "percentual": round(qtd * 100 / total_correcoes) if total_correcoes else 0}
            for nome, qtd in categoria_rows
        ]

        criticidade_rows = dict(db.session.query(
            CorrecaoN2.criticidade,
            func.count(CorrecaoN2.id),
        ).filter(base_filter).group_by(CorrecaoN2.criticidade).all())
        distribuicao_criticidade = [
            {"nome": nome, "qtd": int(criticidade_rows.get(nome, 0)), "percentual": round(criticidade_rows.get(nome, 0) * 100 / total_correcoes) if total_correcoes else 0}
            for nome in ["Alta", "Média", "Baixa"]
        ]


        q = (
            CorrecaoN2.query
            .options(
                load_only(
                    CorrecaoN2.id,
                    CorrecaoN2.titulo,
                    CorrecaoN2.sistema,
                    CorrecaoN2.categoria,
                    CorrecaoN2.criticidade,
                    CorrecaoN2.erro,
                    CorrecaoN2.causa,
                    CorrecaoN2.correcao,
                    CorrecaoN2.acessos,
                    CorrecaoN2.created_at,
                    CorrecaoN2.updated_at
                )
            )
            .filter(base_filter)
        )
        if busca:
            termo = f"%{busca}%"
            q = q.filter(or_(CorrecaoN2.titulo.ilike(termo), CorrecaoN2.sistema.ilike(termo), CorrecaoN2.categoria.ilike(termo), CorrecaoN2.erro.ilike(termo), CorrecaoN2.causa.ilike(termo), CorrecaoN2.correcao.ilike(termo)))
        if categoria:
            q = q.filter(CorrecaoN2.categoria == categoria)
        if criticidade:
            q = q.filter(CorrecaoN2.criticidade == criticidade)

        ordenacoes = {
            "az": CorrecaoN2.titulo.asc(),
            "za": CorrecaoN2.titulo.desc(),
            "criticidade": CorrecaoN2.criticidade.asc(),
            "acessos": CorrecaoN2.acessos.desc(),
        }
        q = q.order_by(
            ordenacoes.get(ordem, CorrecaoN2.updated_at.desc()),
            CorrecaoN2.updated_at.desc()
        )

        paginacao = q.paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )
        itens = paginacao.items

        top_correcoes = (
            CorrecaoN2.query
            .options(load_only(
                CorrecaoN2.id,
                CorrecaoN2.titulo,
                CorrecaoN2.acessos,
                CorrecaoN2.updated_at
            ))
            .filter(base_filter)
            .order_by(
                CorrecaoN2.acessos.desc(),
                CorrecaoN2.updated_at.desc()
            )
            .limit(5)
            .all()
        )

        top_altas = (
            CorrecaoN2.query
            .options(load_only(
                CorrecaoN2.id,
                CorrecaoN2.titulo,
                CorrecaoN2.updated_at
            ))
            .filter(
                base_filter,
                CorrecaoN2.criticidade == "Alta"
            )
            .order_by(CorrecaoN2.updated_at.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "correcoes/list.html",
            itens=itens,
            busca=busca,
            categoria=categoria,
            criticidade=criticidade,
            ordem=ordem,
            categorias=categorias,
            total_correcoes=total_correcoes,
            alta_count=alta_count,
            total_categorias=total_categorias,
            total_acessos=total_acessos,
            distribuicao_criticidade=distribuicao_criticidade,
            distribuicao_categorias=distribuicao_categorias,
            top_correcoes=top_correcoes,
            top_altas=top_altas,
            paginacao=paginacao,
            por_pagina=por_pagina
        )

    @app.route("/correcoes/novo", methods=["GET", "POST"])
    @admin_required
    def correcoes_novo():
        return salvar_correcao()

    @app.route("/correcoes/<int:id>")
    def correcoes_ver(id):
        item = CorrecaoN2.query.filter_by(id=id, deleted_at=None).first_or_404()

        item.acessos = (item.acessos or 0) + 1

        hoje = datetime.utcnow().date()

        acesso_dia = CorrecaoAcesso.query.filter_by(
            correcao_id=item.id,
            data_acesso=hoje
        ).first()

        if acesso_dia:
            acesso_dia.quantidade = (acesso_dia.quantidade or 0) + 1
        else:
            db.session.add(CorrecaoAcesso(
                correcao_id=item.id,
                data_acesso=hoje,
                quantidade=1
            ))

        db.session.commit()

        return render_template("correcoes/view.html", item=item)

    @app.route("/correcoes/<int:id>/editar", methods=["GET", "POST"])
    @admin_required
    def correcoes_editar(id):
        return salvar_correcao(CorrecaoN2.query.filter_by(id=id, deleted_at=None).first_or_404())

    def salvar_correcao(item=None):
        if request.method == "POST":
            if item is None: item = CorrecaoN2(); db.session.add(item)
            for campo in ["titulo", "sistema", "categoria", "criticidade", "erro", "causa", "correcao"]:
                setattr(item, campo, request.form.get(campo))
            item.updated_at = datetime.utcnow(); db.session.flush()
            for f in request.files.getlist("anexos"):
                if f and f.filename and allowed_image(f.filename):
                    db.session.add(AnexoCorrecao(correcao_id=item.id, nome_arquivo=secure_filename(f.filename), mime_type=f.mimetype, conteudo=f.read()))
            db.session.commit(); flash("Correção salva com sucesso.", "success")
            return redirect(url_for("correcoes_ver", id=item.id))
        return render_template("correcoes/form.html", item=item)

    @app.route("/correcoes/<int:id>/excluir", methods=["POST"])
    @admin_required
    def correcoes_excluir(id):
        item = CorrecaoN2.query.get_or_404(id); item.deleted_at = datetime.utcnow(); db.session.commit(); flash("Correção removida.", "success"); return redirect(url_for("correcoes_listar"))

    @app.route("/anexos/<int:id>")
    def anexo_ver(id):
        anexo = AnexoCorrecao.query.filter_by(id=id, deleted_at=None).first_or_404()
        return send_file(io.BytesIO(anexo.conteudo), mimetype=anexo.mime_type, download_name=anexo.nome_arquivo)

    @app.route("/anexos/<int:id>/excluir", methods=["POST"])
    @admin_required
    def anexo_excluir(id):
        anexo = AnexoCorrecao.query.get_or_404(id); anexo.deleted_at = datetime.utcnow(); db.session.commit(); flash("Anexo removido.", "success"); return redirect(url_for("correcoes_editar", id=anexo.correcao_id))

    @app.route("/correcoes/exportar")
    @admin_required
    def correcoes_exportar():
        dados = [{k:getattr(c,k) for k in ["titulo","sistema","erro","causa","correcao","categoria","criticidade"]} | {"created_at": c.created_at.isoformat(), "updated_at": c.updated_at.isoformat()} for c in CorrecaoN2.query.filter_by(deleted_at=None).all()]
        return send_file(io.BytesIO(json.dumps(dados, ensure_ascii=False, indent=2).encode()), mimetype="application/json", as_attachment=True, download_name="correcoes_n2.json")

    @app.route("/correcoes/importar", methods=["POST"])
    @admin_required
    def correcoes_importar():
        data = json.load(request.files["arquivo"])
        for row in data:
            if "rotinaNome" in row:
                item = CorrecaoN2(titulo=row.get("rotinaNome") or "Sem título", sistema=row.get("versao") or "", erro=row.get("comentario") or "", causa="Não informado", correcao=row.get("solucao") or "", categoria="Rotina", criticidade="Baixa")
            else:
                item = CorrecaoN2(titulo=row.get("titulo") or "Sem título", sistema=row.get("sistema"), erro=row.get("erro"), causa=row.get("causa"), correcao=row.get("correcao"), categoria=row.get("categoria"), criticidade=row.get("criticidade") or "Baixa")
            db.session.add(item)
        db.session.commit(); flash("Importação concluída.", "success"); return redirect(url_for("correcoes_listar"))

    @app.route("/scripts")
    def scripts_listar():
        busca = (request.args.get("busca") or "").strip()
        banco = (request.args.get("banco") or "").strip()
        ordem = (request.args.get("ordem") or "recentes").strip()

        pagina = request.args.get("pagina", 1, type=int)
        por_pagina = request.args.get("por_pagina", 12, type=int)
        pagina = max(pagina or 1, 1)
        por_pagina = min(max(por_pagina or 12, 6), 48)

        base_filter = ScriptSQL.deleted_at.is_(None)

        resumo = db.session.query(
            func.count(ScriptSQL.id),
            func.sum(
                case(
                    (
                        or_(
                            ScriptSQL.tipo_banco.ilike("%SQL Server%"),
                            ScriptSQL.tipo_banco.ilike("SQL")
                        ),
                        1
                    ),
                    else_=0
                )
            ),
            func.coalesce(func.sum(ScriptSQL.acessos), 0),
        ).filter(base_filter).first()

        total_scripts = int(resumo[0] or 0)
        sql_server_count = int(resumo[1] or 0)
        total_acessos = int(resumo[2] or 0)

        total_consultas = (
            db.session.query(func.count(ConsultaSQL.id))
            .join(ScriptSQL, ConsultaSQL.script_id == ScriptSQL.id)
            .filter(base_filter)
            .scalar()
            or 0
        )

        banco_rows = (
            db.session.query(
                ScriptSQL.tipo_banco,
                func.count(ScriptSQL.id)
            )
            .filter(
                base_filter,
                ScriptSQL.tipo_banco.isnot(None)
            )
            .group_by(ScriptSQL.tipo_banco)
            .order_by(ScriptSQL.tipo_banco)
            .all()
        )

        bancos_disponiveis = [nome for nome, _ in banco_rows]
        distribuicao_bancos = [
            {
                "nome": nome,
                "qtd": int(qtd or 0),
                "percentual": (
                    round((int(qtd or 0) * 100) / total_scripts)
                    if total_scripts else 0
                )
            }
            for nome, qtd in banco_rows
        ]


        q = (
            ScriptSQL.query
            .options(
                load_only(
                    ScriptSQL.id,
                    ScriptSQL.titulo,
                    ScriptSQL.tipo_banco,
                    ScriptSQL.descricao,
                    ScriptSQL.observacoes,
                    ScriptSQL.acessos,
                    ScriptSQL.created_at,
                    ScriptSQL.updated_at
                )
            )
            .filter(base_filter)
        )

        if busca:
            termo = f"%{busca}%"
            q = q.filter(
                or_(
                    ScriptSQL.titulo.ilike(termo),
                    ScriptSQL.tipo_banco.ilike(termo),
                    ScriptSQL.descricao.ilike(termo),
                    ScriptSQL.observacoes.ilike(termo)
                )
            )

        if banco:
            q = q.filter(ScriptSQL.tipo_banco == banco)

        if ordem == "az":
            q = q.order_by(ScriptSQL.titulo.asc())
        elif ordem == "za":
            q = q.order_by(ScriptSQL.titulo.desc())
        elif ordem == "banco":
            q = q.order_by(
                ScriptSQL.tipo_banco.asc(),
                ScriptSQL.titulo.asc()
            )
        elif ordem == "acessos":
            q = q.order_by(
                ScriptSQL.acessos.desc(),
                ScriptSQL.updated_at.desc()
            )
        else:
            q = q.order_by(ScriptSQL.updated_at.desc())

        paginacao = q.paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )
        itens = paginacao.items

        ids_scripts = [item.id for item in itens]
        contagens_consultas = {}

        if ids_scripts:
            contagem_rows = (
                db.session.query(
                    ConsultaSQL.script_id,
                    func.count(ConsultaSQL.id)
                )
                .filter(ConsultaSQL.script_id.in_(ids_scripts))
                .group_by(ConsultaSQL.script_id)
                .all()
            )

            contagens_consultas = {
                script_id: int(quantidade or 0)
                for script_id, quantidade in contagem_rows
            }

        top_scripts = (
            ScriptSQL.query
            .options(
                load_only(
                    ScriptSQL.id,
                    ScriptSQL.titulo,
                    ScriptSQL.acessos,
                    ScriptSQL.updated_at
                )
            )
            .filter(base_filter)
            .order_by(
                ScriptSQL.acessos.desc(),
                ScriptSQL.updated_at.desc()
            )
            .limit(5)
            .all()
        )

        top_consultas = (
            db.session.query(
                ScriptSQL,
                func.count(ConsultaSQL.id).label("quantidade_consultas")
            )
            .outerjoin(
                ConsultaSQL,
                ConsultaSQL.script_id == ScriptSQL.id
            )
            .filter(base_filter)
            .group_by(ScriptSQL.id)
            .order_by(
                func.count(ConsultaSQL.id).desc(),
                ScriptSQL.updated_at.desc()
            )
            .limit(5)
            .all()
        )

        return render_template(
            "scripts/list.html",
            itens=itens,
            busca=busca,
            banco=banco,
            ordem=ordem,
            bancos_disponiveis=bancos_disponiveis,
            total_scripts=total_scripts,
            sql_server_count=sql_server_count,
            total_consultas=int(total_consultas),
            total_acessos=total_acessos,
            favoritos=0,
            distribuicao_bancos=distribuicao_bancos,
            top_scripts=top_scripts,
            top_consultas=top_consultas,
            contagens_consultas=contagens_consultas,
            paginacao=paginacao,
            por_pagina=por_pagina
        )

    @app.route("/scripts/novo", methods=["GET", "POST"])
    @admin_required
    def scripts_novo(): return salvar_script()

    @app.route("/scripts/<int:id>")
    def scripts_ver(id):
        item = ScriptSQL.query.filter_by(id=id, deleted_at=None).first_or_404()

        item.acessos = (item.acessos or 0) + 1

        hoje = datetime.utcnow().date()

        acesso_dia = ScriptAcesso.query.filter_by(
            script_id=item.id,
            data_acesso=hoje
        ).first()

        if acesso_dia:
            acesso_dia.quantidade = (acesso_dia.quantidade or 0) + 1
        else:
            db.session.add(ScriptAcesso(
                script_id=item.id,
                data_acesso=hoje,
                quantidade=1
            ))

        db.session.commit()
        return render_template("scripts/view.html", item=item)

    @app.route("/scripts/<int:id>/editar", methods=["GET", "POST"])
    @admin_required
    def scripts_editar(id): return salvar_script(ScriptSQL.query.filter_by(id=id, deleted_at=None).first_or_404())

    def salvar_script(item=None):
        if request.method == "POST":
            titulo = (request.form.get("titulo") or "").strip()
            tipo_banco = (request.form.get("tipo_banco") or request.form.get("tipo") or "").strip()
            descricao = request.form.get("descricao") or ""
            observacoes = request.form.get("observacoes") or ""

            if not titulo:
                flash("Informe o título do script.", "warning")
                return render_template("scripts/form.html", item=item)

            if not tipo_banco:
                tipo_banco = "Não informado"

            if item is None:
                item = ScriptSQL()
                db.session.add(item)

            item.titulo = titulo
            item.tipo_banco = tipo_banco
            item.descricao = descricao
            item.observacoes = observacoes
            item.updated_at = datetime.utcnow()

            db.session.flush()

            ConsultaSQL.query.filter_by(script_id=item.id).delete()

            titulos = request.form.getlist("titulo_consulta[]") or request.form.getlist("consulta_titulo[]")
            codigos = request.form.getlist("codigo_sql[]") or request.form.getlist("consulta_sql[]")

            for i, (t, c) in enumerate(zip(titulos, codigos)):
                t = (t or "").strip()
                c = (c or "").strip()
                if t or c:
                    db.session.add(ConsultaSQL(
                        script_id=item.id,
                        titulo_consulta=t or f"Consulta {i + 1}",
                        codigo_sql=c,
                        ordem=i
                    ))

            db.session.commit()
            flash("Script salvo.", "success")
            return redirect(url_for("scripts_ver", id=item.id))
        return render_template("scripts/form.html", item=item)

    @app.route("/scripts/<int:id>/excluir", methods=["POST"])
    @admin_required
    def scripts_excluir(id):
        item=ScriptSQL.query.get_or_404(id); item.deleted_at=datetime.utcnow(); db.session.commit(); flash("Script removido.", "success"); return redirect(url_for("scripts_listar"))

    @app.route("/bancos")
    def bancos_listar():
        return render_template("bancos/list.html", itens=BancoMapeado.query.filter_by(deleted_at=None).order_by(BancoMapeado.nome).all())

    @app.route("/bancos/novo", methods=["GET","POST"])
    @app.route("/bancos/<int:id>/editar", methods=["GET","POST"])
    @admin_required
    def banco_form(id=None):
        item = BancoMapeado.query.get(id) if id else BancoMapeado()
        if request.method == "POST":
            if not id: db.session.add(item)
            item.nome=request.form.get("nome"); item.tipo_banco=request.form.get("tipo_banco"); item.descricao=request.form.get("descricao"); item.observacoes=request.form.get("observacoes"); item.updated_at=datetime.utcnow(); db.session.commit(); flash("Banco salvo.","success"); return redirect(url_for("bancos_listar"))
        return render_template("bancos/form.html", item=item)

    @app.route("/bancos/<int:id>/excluir", methods=["POST"])
    @admin_required
    def banco_excluir(id):
        item=BancoMapeado.query.get_or_404(id); item.deleted_at=datetime.utcnow(); db.session.commit(); return redirect(url_for("bancos_listar"))

    def _listar_arquivos_modulo(modulo, titulo):
        busca = (request.args.get("busca") or "").strip()
        tipo = (request.args.get("tipo") or "").strip()
        ordem = (request.args.get("ordem") or "recentes").strip()

        pagina = request.args.get("pagina", 1, type=int)
        por_pagina = request.args.get("por_pagina", 12, type=int)
        pagina = max(pagina or 1, 1)
        por_pagina = min(max(por_pagina or 12, 6), 48)

        base_filter = (ArquivoDownload.modulo == modulo, ArquivoDownload.deleted_at.is_(None))

        resumo = db.session.query(
            func.count(ArquivoDownload.id),
            func.coalesce(func.sum(ArquivoDownload.downloads), 0),
            func.count(func.distinct(ArquivoDownload.tipo)),
        ).filter(*base_filter).first()
        total_ferramentas = int(resumo[0] or 0)
        total_downloads = int(resumo[1] or 0)
        total_tipos = int(resumo[2] or 0)

        tipo_rows = db.session.query(ArquivoDownload.tipo, func.count(ArquivoDownload.id)).filter(*base_filter, ArquivoDownload.tipo.isnot(None)).group_by(ArquivoDownload.tipo).order_by(ArquivoDownload.tipo).all()
        tipos_disponiveis = [nome for nome, _ in tipo_rows]
        distribuicao_tipos = [
            {"nome": nome, "qtd": qtd, "percentual": round(qtd * 100 / total_ferramentas) if total_ferramentas else 0}
            for nome, qtd in tipo_rows
        ]

        mais_baixada = ArquivoDownload.query.filter(*base_filter).order_by(ArquivoDownload.downloads.desc(), ArquivoDownload.updated_at.desc()).first()


        q = (
            ArquivoDownload.query
            .options(
                load_only(
                    ArquivoDownload.id,
                    ArquivoDownload.modulo,
                    ArquivoDownload.nome,
                    ArquivoDownload.tipo,
                    ArquivoDownload.link_download,
                    ArquivoDownload.downloads,
                    ArquivoDownload.created_at,
                    ArquivoDownload.updated_at
                )
            )
            .filter(*base_filter)
        )
        if busca:
            termo = f"%{busca}%"
            q = q.filter(or_(ArquivoDownload.nome.ilike(termo), ArquivoDownload.tipo.ilike(termo)))
        if tipo:
            q = q.filter(ArquivoDownload.tipo == tipo)
        if ordem == "az":
            q = q.order_by(ArquivoDownload.nome.asc())
        elif ordem == "za":
            q = q.order_by(ArquivoDownload.nome.desc())
        elif ordem == "downloads":
            q = q.order_by(ArquivoDownload.downloads.desc(), ArquivoDownload.updated_at.desc())
        elif ordem == "tipo":
            q = q.order_by(ArquivoDownload.tipo.asc(), ArquivoDownload.nome.asc())
        else:
            q = q.order_by(ArquivoDownload.updated_at.desc())

        paginacao = q.paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )
        itens = paginacao.items

        top_downloads = (
            ArquivoDownload.query
            .options(load_only(
                ArquivoDownload.id,
                ArquivoDownload.modulo,
                ArquivoDownload.nome,
                ArquivoDownload.downloads,
                ArquivoDownload.updated_at
            ))
            .filter(*base_filter)
            .order_by(
                ArquivoDownload.downloads.desc(),
                ArquivoDownload.updated_at.desc()
            )
            .limit(5)
            .all()
        )

        recentes = (
            ArquivoDownload.query
            .options(load_only(
                ArquivoDownload.id,
                ArquivoDownload.modulo,
                ArquivoDownload.nome,
                ArquivoDownload.created_at
            ))
            .filter(*base_filter)
            .order_by(ArquivoDownload.created_at.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "datasync/list.html",
            titulo=titulo,
            modulo=modulo,
            itens=itens,
            busca=busca,
            tipo=tipo,
            ordem=ordem,
            tipos_disponiveis=tipos_disponiveis,
            total_ferramentas=total_ferramentas,
            total_downloads=total_downloads,
            total_tipos=total_tipos,
            mais_baixada=mais_baixada,
            distribuicao_tipos=distribuicao_tipos,
            top_downloads=top_downloads,
            recentes=recentes,
            paginacao=paginacao,
            por_pagina=por_pagina
        )

    @app.route("/datasync")
    def datasync():
        return _listar_arquivos_modulo("datasync", "DataSync")

    @app.route("/conversao")
    def conversao():
        return _listar_arquivos_modulo("conversao", "Ferramentas de Conversão de Dados")

    def _modulo_redirect(modulo):
        return "datasync" if modulo == "datasync" else "conversao"

    def _modulo_titulo(modulo):
        return "DataSync" if modulo == "datasync" else "Ferramentas de Conversão de Dados"

    @app.route("/arquivos/<modulo>/novo", methods=["GET", "POST"])
    @admin_required
    def arquivo_novo(modulo):
        if modulo not in ["datasync", "conversao"]:
            abort(404)

        if request.method == "POST":
            nome = (request.form.get("nome") or "").strip()
            tipo = (request.form.get("tipo") or "").strip()
            link_download = (request.form.get("link_download") or "").strip()

            if not nome or not tipo or not link_download:
                flash("Preencha nome, tipo e link para download.", "warning")
                return render_template("datasync/form.html", item=None, modulo=modulo, titulo=_modulo_titulo(modulo))

            item = ArquivoDownload(
                modulo=modulo,
                nome=nome,
                tipo=tipo,
                link_download=link_download,
                downloads=0
            )
            db.session.add(item)
            db.session.commit()
            flash("Link cadastrado com sucesso.", "success")
            return redirect(url_for(_modulo_redirect(modulo)))

        return render_template("datasync/form.html", item=None, modulo=modulo, titulo=_modulo_titulo(modulo))

    @app.route("/arquivos/<modulo>/<int:id>/editar", methods=["GET", "POST"])
    @admin_required
    def arquivo_editar(modulo, id):
        if modulo not in ["datasync", "conversao"]:
            abort(404)

        item = ArquivoDownload.query.filter_by(
            id=id,
            modulo=modulo,
            deleted_at=None
        ).first_or_404()

        if request.method == "POST":
            nome = (request.form.get("nome") or "").strip()
            tipo = (request.form.get("tipo") or "").strip()
            link_download = (request.form.get("link_download") or "").strip()

            if not nome or not tipo or not link_download:
                flash("Preencha nome, tipo e link para download.", "warning")
                return render_template("datasync/form.html", item=item, modulo=modulo, titulo=_modulo_titulo(modulo))

            item.nome = nome
            item.tipo = tipo
            item.link_download = link_download
            item.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Link atualizado com sucesso.", "success")
            return redirect(url_for(_modulo_redirect(modulo)))

        return render_template("datasync/form.html", item=item, modulo=modulo, titulo=_modulo_titulo(modulo))

    @app.route("/arquivos/<modulo>/<int:id>/excluir", methods=["POST"])
    @admin_required
    def arquivo_excluir(modulo, id):
        if modulo not in ["datasync", "conversao"]:
            abort(404)

        item = ArquivoDownload.query.filter_by(
            id=id,
            modulo=modulo,
            deleted_at=None
        ).first_or_404()
        item.deleted_at = datetime.utcnow()
        db.session.commit()
        flash("Link removido com sucesso.", "success")
        return redirect(url_for(_modulo_redirect(modulo)))

    @app.route("/arquivos/<modulo>/<int:id>/download")
    def arquivo_download_link(modulo, id):
        if modulo not in ["datasync", "conversao"]:
            abort(404)

        item = ArquivoDownload.query.filter_by(
            id=id,
            modulo=modulo,
            deleted_at=None
        ).first_or_404()
        item.downloads = (item.downloads or 0) + 1

        hoje = datetime.utcnow().date()
        acesso_dia = ArquivoDownloadAcesso.query.filter_by(
            arquivo_id=item.id,
            data_acesso=hoje
        ).first()

        if acesso_dia:
            acesso_dia.quantidade = (acesso_dia.quantidade or 0) + 1
        else:
            db.session.add(ArquivoDownloadAcesso(
                arquivo_id=item.id,
                data_acesso=hoje,
                quantidade=1
            ))

        db.session.commit()

        if not item.link_download:
            flash("Este item não possui link de download cadastrado.", "warning")
            return redirect(url_for(_modulo_redirect(modulo)))

        return redirect(item.link_download)

    @app.route("/gerador-identificador")
    def gerador():
        return render_template("conversao/identificador.html")

    @app.route("/api/identificador", methods=["POST"])
    def api_identificador():
        dados = request.get_json(silent=True) or {}
        linha = (dados.get("linha") or "").strip()

        if not linha:
            return jsonify({
                "ok": False,
                "erro": "Digite ou cole uma linha antes de gerar."
            }), 400

        numero, identificador = extrair_dados_identificador(linha)

        if not numero:
            return jsonify({
                "ok": False,
                "erro": "Não foi possível localizar um número válido na linha."
            }), 422

        if not identificador:
            return jsonify({
                "ok": False,
                "erro": "Não foi possível gerar o identificador a partir do texto informado."
            }), 422

        return jsonify({
            "ok": True,
            "numero": numero,
            "identificador": identificador
        })

if __name__ == "__main__":
    create_app().run(debug=True)
