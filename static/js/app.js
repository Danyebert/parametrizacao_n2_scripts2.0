// ===========================================
// Parametrização N2 Scripts
// app.js
// ===========================================

// ----------------------------
// Tema
// ----------------------------
const html = document.documentElement;

const temaSalvo = localStorage.getItem("theme");

if (temaSalvo) {
    html.setAttribute("data-bs-theme", temaSalvo);
}

document.getElementById("toggleTheme")?.addEventListener("click", () => {

    const novoTema =
        html.getAttribute("data-bs-theme") === "dark"
            ? "light"
            : "dark";

    html.setAttribute("data-bs-theme", novoTema);

    localStorage.setItem("theme", novoTema);

    alterarTemaEditores();
});

// ----------------------------
// Sidebar
// ----------------------------

document.getElementById("toggleSidebar")?.addEventListener("click", () => {

    const sidebar = document.getElementById("sidebar");

    if (window.innerWidth < 900) {
        sidebar.classList.toggle("show");
    } else {
        sidebar.classList.toggle("collapsed");
    }

});

// ----------------------------
// CodeMirror
// ----------------------------

const editoresSQL = [];

function temaEditorAtual() {

    return html.getAttribute("data-bs-theme") === "dark"
        ? "darcula"
        : "default";

}

function initCodeMirror(selector = ".codemirror-sql") {

    document.querySelectorAll(selector).forEach(textarea => {

        if (textarea.dataset.cm) return;

        textarea.dataset.cm = "1";

        const editor = CodeMirror.fromTextArea(textarea, {

            mode: "text/x-sql",

            theme: temaEditorAtual(),

            lineNumbers: true,

            lineWrapping: true,

            indentUnit: 4,

            tabSize: 4,

            indentWithTabs: false,

            smartIndent: true,

            matchBrackets: true,

            autoCloseBrackets: true,

            styleActiveLine: true,

            foldGutter: true,

            gutters: [
                "CodeMirror-linenumbers",
                "CodeMirror-foldgutter"
            ],

            extraKeys: {

                "F11": function(cm) {
                    cm.setOption("fullScreen", !cm.getOption("fullScreen"));
                },

                "Esc": function(cm) {
                    if (cm.getOption("fullScreen")) {
                        cm.setOption("fullScreen", false);
                    }
                }

            }

        });

        editoresSQL.push(editor);

    });

}

function alterarTemaEditores() {

    editoresSQL.forEach(editor => {

        editor.setOption(
            "theme",
            temaEditorAtual()
        );

    });

}

// ----------------------------
// SQL Formatter
// ----------------------------

function getDialetoSQL() {

    const banco =
        document.querySelector('[name="tipo_banco"]')?.value;

    const mapa = {

        "SQL Server": "transactsql",

        "MySQL": "mysql",

        "PostgreSQL": "postgresql",

        "Oracle": "plsql",

        "SQLite": "sqlite",

        "Firebird": "sql",

        "Access": "sql"

    };

    return mapa[banco] || "sql";

}

function formatarSQL(botao) {

    const consulta = botao.closest(".consulta");

    const editor =
        consulta.querySelector(".CodeMirror").CodeMirror;

    try {

        editor.setValue(

            sqlFormatter.format(

                editor.getValue(),

                {

                    language: getDialetoSQL(),

                    keywordCase: "upper",

                    indentStyle: "standard",

                    linesBetweenQueries: 2

                }

            )

        );

        editor.refresh();

    } catch (e) {

        console.error(e);

        alert("Erro ao formatar SQL.");

    }

}

function copiarSQL(botao) {

    const consulta = botao.closest(".consulta");

    const editor =
        consulta.querySelector(".CodeMirror").CodeMirror;

    navigator.clipboard.writeText(editor.getValue());

    const texto = botao.innerHTML;

    botao.innerHTML =
        '<i class="bi bi-check2"></i> Copiado';

    setTimeout(() => {

        botao.innerHTML = texto;

    }, 1500);

}

function telaCheiaSQL(botao) {

    const consulta = botao.closest(".consulta");

    consulta.classList.toggle("sql-fullscreen");

    const editor =
        consulta.querySelector(".CodeMirror").CodeMirror;

    setTimeout(() => {

        editor.refresh();

    }, 200);

}

// ----------------------------
// Pesquisa dinâmica Scripts
// ----------------------------

function pesquisarScripts() {

    const campo = document.getElementById("pesquisaScripts");

    if (!campo) return;

    const filtro = campo.value.toLowerCase();

    document.querySelectorAll(".script-card").forEach(card => {

        card.style.display =
            card.innerText.toLowerCase().includes(filtro)
                ? ""
                : "none";

    });

}

// ----------------------------
// Filtro Banco
// ----------------------------

function filtrarBanco() {

    const select = document.getElementById("filtroBanco");

    if (!select) return;

    const valor = select.value;

    document.querySelectorAll(".script-card").forEach(card => {

        if (
            valor === "" ||
            card.dataset.banco === valor
        ) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });

}

// ----------------------------
// Contadores animados
// ----------------------------

function animarContadores() {

    document.querySelectorAll(".counter").forEach(counter => {

        const destino =
            parseInt(counter.dataset.value);

        if (isNaN(destino)) return;

        let atual = 0;

        const incremento =
            Math.max(1, Math.ceil(destino / 50));

        const timer = setInterval(() => {

            atual += incremento;

            if (atual >= destino) {

                atual = destino;

                clearInterval(timer);

            }

            counter.innerText = atual;

        }, 20);

    });

}

// ----------------------------
// Hover cards
// ----------------------------

document.addEventListener("mouseover", e => {

    const card = e.target.closest(".script-card");

    if (!card) return;

    card.classList.add("hover");

});

document.addEventListener("mouseout", e => {

    const card = e.target.closest(".script-card");

    if (!card) return;

    card.classList.remove("hover");

});

// ----------------------------
// Inicialização
// ----------------------------

document.addEventListener("DOMContentLoaded", () => {

    initCodeMirror();

    animarContadores();

    document
        .getElementById("pesquisaScripts")
        ?.addEventListener("keyup", pesquisarScripts);

    document
        .getElementById("filtroBanco")
        ?.addEventListener("change", filtrarBanco);

});