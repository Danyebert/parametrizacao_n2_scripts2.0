import os, io, json, zipfile, unicodedata, re
from datetime import datetime
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func, text
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
    anexos = db.relationship("AnexoCorrecao", backref="correcao", lazy=True)

class AnexoCorrecao(db.Model, TimestampMixin):
    __tablename__ = "anexos_correcoes"
    id = db.Column(db.Integer, primary_key=True)
    correcao_id = db.Column(db.Integer, db.ForeignKey("correcoes_n2.id"), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.LargeBinary, nullable=False)

class ScriptSQL(db.Model, TimestampMixin):
    __tablename__ = "scripts_sql"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    tipo_banco = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    acessos = db.Column(db.Integer, default=0, nullable=False)
    consultas = db.relationship("ConsultaSQL", backref="script", lazy=True, cascade="all, delete-orphan")

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



def ensure_schema_updates():
    """Aplica pequenas alterações de schema que o db.create_all() não faz em tabelas existentes."""
    try:
        db.session.execute(text("ALTER TABLE scripts_sql ADD COLUMN IF NOT EXISTS acessos INTEGER DEFAULT 0 NOT NULL"))
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
    db.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_schema_updates()
        create_default_admin()

    register_routes(app)
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


def get_file_listing(modulo):
    return ArquivoDownload.query.filter_by(
        modulo=modulo,
        deleted_at=None
    ).order_by(ArquivoDownload.nome).all()


def register_routes(app):
    @app.context_processor
    def inject_globals():
        return {"is_admin": is_admin(),
                "APP_VERSION": "2.3.2",
                "APP_BUILD": "2026-07-08",
                "APP_COPYRIGHT": "© 2026 Parametrização N2"}

    @app.route("/")
    def dashboard():
        dias = int(request.args.get("dias", 7))

        ultimas_correcoes = CorrecaoN2.query.filter_by(
            deleted_at=None
        ).order_by(CorrecaoN2.updated_at.desc()).limit(5).all()

        ultimos_scripts = ScriptSQL.query.filter_by(
            deleted_at=None
        ).order_by(ScriptSQL.updated_at.desc()).limit(5).all()

        arquivos_mais_baixados = ArquivoDownload.query.filter_by(
            deleted_at=None
        ).order_by(ArquivoDownload.downloads.desc()).limit(5).all()

        return render_template(
            "dashboard.html",
            correcoes=CorrecaoN2.query.filter_by(deleted_at=None).count(),
            scripts=ScriptSQL.query.filter_by(deleted_at=None).count(),
            bancos=BancoMapeado.query.filter_by(deleted_at=None).count(),
            downloads=ArquivoDownload.query.filter_by(deleted_at=None).count(),
            dias=dias,
            ultimas_correcoes=ultimas_correcoes,
            ultimos_scripts=ultimos_scripts,
            arquivos_mais_baixados=arquivos_mais_baixados
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
        q = CorrecaoN2.query.filter_by(deleted_at=None)
        busca = request.args.get("busca", "").strip(); categoria = request.args.get("categoria", ""); criticidade = request.args.get("criticidade", "")
        if busca: q = q.filter(or_(CorrecaoN2.titulo.ilike(f"%{busca}%"), CorrecaoN2.sistema.ilike(f"%{busca}%"), CorrecaoN2.erro.ilike(f"%{busca}%")))
        if categoria: q = q.filter(CorrecaoN2.categoria == categoria)
        if criticidade: q = q.filter(CorrecaoN2.criticidade == criticidade)
        categorias = [r[0] for r in db.session.query(CorrecaoN2.categoria).filter(CorrecaoN2.deleted_at==None, CorrecaoN2.categoria!=None).distinct()]
        return render_template("correcoes/list.html", itens=q.order_by(CorrecaoN2.updated_at.desc()).all(), categorias=categorias)

    @app.route("/correcoes/novo", methods=["GET", "POST"])
    @admin_required
    def correcoes_novo():
        return salvar_correcao()

    @app.route("/correcoes/<int:id>")
    def correcoes_ver(id):
        item = CorrecaoN2.query.filter_by(id=id, deleted_at=None).first_or_404()
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

        base = ScriptSQL.query.filter_by(deleted_at=None)

        bancos_disponiveis = [
            r[0] for r in db.session.query(ScriptSQL.tipo_banco)
            .filter(ScriptSQL.deleted_at == None, ScriptSQL.tipo_banco != None)
            .distinct()
            .order_by(ScriptSQL.tipo_banco)
            .all()
        ]

        total_scripts = base.count()
        sql_server_count = base.filter(
            or_(
                ScriptSQL.tipo_banco.ilike("%SQL Server%"),
                ScriptSQL.tipo_banco.ilike("SQL")
            )
        ).count()

        total_consultas = db.session.query(ConsultaSQL).join(ScriptSQL).filter(
            ScriptSQL.deleted_at == None
        ).count()

        total_acessos = db.session.query(func.coalesce(func.sum(ScriptSQL.acessos), 0)).filter(ScriptSQL.deleted_at == None).scalar() or 0

        distribuicao_bancos = []
        for nome_banco in bancos_disponiveis:
            qtd = base.filter(ScriptSQL.tipo_banco == nome_banco).count()
            percentual = round((qtd / total_scripts) * 100) if total_scripts else 0
            distribuicao_bancos.append({
                "nome": nome_banco,
                "qtd": qtd,
                "percentual": percentual
            })

        q = base

        if busca:
            q = q.filter(or_(
                ScriptSQL.titulo.ilike(f"%{busca}%"),
                ScriptSQL.tipo_banco.ilike(f"%{busca}%"),
                ScriptSQL.descricao.ilike(f"%{busca}%"),
                ScriptSQL.observacoes.ilike(f"%{busca}%")
            ))

        if banco:
            q = q.filter(ScriptSQL.tipo_banco == banco)

        if ordem == "az":
            q = q.order_by(ScriptSQL.titulo.asc())
        elif ordem == "za":
            q = q.order_by(ScriptSQL.titulo.desc())
        elif ordem == "banco":
            q = q.order_by(ScriptSQL.tipo_banco.asc(), ScriptSQL.titulo.asc())
        elif ordem == "acessos":
            q = q.order_by(ScriptSQL.acessos.desc(), ScriptSQL.updated_at.desc())
        else:
            q = q.order_by(ScriptSQL.updated_at.desc())

        itens = q.all()

        todos_scripts = base.all()

        top_scripts = ScriptSQL.query.filter_by(deleted_at=None).order_by(
            ScriptSQL.acessos.desc(),
            ScriptSQL.updated_at.desc()
        ).limit(5).all()

        top_consultas = sorted(
            todos_scripts,
            key=lambda s: len(s.consultas),
            reverse=True
        )[:5]

        return render_template(
            "scripts/list.html",
            itens=itens,
            busca=busca,
            banco=banco,
            ordem=ordem,
            bancos_disponiveis=bancos_disponiveis,
            total_scripts=total_scripts,
            sql_server_count=sql_server_count,
            total_consultas=total_consultas,
            total_acessos=total_acessos,
            favoritos=0,
            distribuicao_bancos=distribuicao_bancos,
            top_scripts=top_scripts,
            top_consultas=top_consultas
        )

    @app.route("/scripts/novo", methods=["GET", "POST"])
    @admin_required
    def scripts_novo(): return salvar_script()

    @app.route("/scripts/<int:id>")
    def scripts_ver(id):
        item = ScriptSQL.query.filter_by(id=id, deleted_at=None).first_or_404()
        item.acessos = (item.acessos or 0) + 1
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

    @app.route("/datasync")
    def datasync():
        return render_template(
            "datasync/list.html",
            titulo="DataSync",
            modulo="datasync",
            itens=get_file_listing("datasync")
        )

    @app.route("/conversao")
    def conversao():
        return render_template(
            "datasync/list.html",
            titulo="Ferramentas de Conversão de Dados",
            modulo="conversao",
            itens=get_file_listing("conversao")
        )

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
        db.session.commit()

        if not item.link_download:
            flash("Este item não possui link de download cadastrado.", "warning")
            return redirect(url_for(_modulo_redirect(modulo)))

        return redirect(item.link_download)

    @app.route("/gerador-identificador")
    def gerador(): return render_template("conversao/identificador.html")

    @app.route("/api/identificador", methods=["POST"])
    def api_identificador():
        linha = request.json.get("linha", "")
        partes = [p.strip() for p in linha.split("-")]
        numero = next((p for p in partes if p.isdigit()), "")
        nome_cidade = "".join(partes[2:]) if len(partes) >= 3 else linha
        return jsonify({"numero": numero, "identificador": normalize_identificador(nome_cidade)})

if __name__ == "__main__":
    create_app().run(debug=True)
