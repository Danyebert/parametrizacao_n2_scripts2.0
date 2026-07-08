// ==============================
// Parametrização N2 Scripts
// app.js
// ==============================

// ----------------------------
// Tema do sistema
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

        if (textarea.dataset.cm) {
            return;
        }

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

                "F11": function (cm) {

                    cm.setOption(
                        "fullScreen",
                        !cm.getOption("fullScreen")
                    );

                },

                "Esc": function (cm) {

                    if (cm.getOption("fullScreen")) {
                        cm.setOption("fullScreen", false);
                    }

                }

            }

        });

        editoresSQL.push(editor);

    });

}

// ----------------------------
// Troca tema editor
// ----------------------------

function alterarTemaEditores() {

    editoresSQL.forEach(editor => {

        editor.setOption(
            "theme",
            temaEditorAtual()
        );

    });

}

// ----------------------------
// Copiar SQL
// ----------------------------

function copiarSQL(botao) {

    const consulta = botao.closest(".consulta");

    const editor =
        consulta.querySelector(".CodeMirror").CodeMirror;

    navigator.clipboard.writeText(editor.getValue());

    const texto = botao.innerHTML;

    botao.innerHTML =
        '<i class="bi bi-check-lg"></i> Copiado';

    setTimeout(() => {

        botao.innerHTML = texto;

    }, 1500);

}

// ----------------------------
// Tela cheia
// ----------------------------

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
// Formatter
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

        const sql = sqlFormatter.format(

            editor.getValue(),

            {

                language: getDialetoSQL(),

                keywordCase: "upper",

                indentStyle: "standard",

                linesBetweenQueries: 2

            }

        );

        editor.setValue(sql);

        editor.refresh();

    } catch (erro) {

        alert("Erro ao formatar SQL.");

        console.error(erro);

    }

}

// ----------------------------
// Copiar texto
// ----------------------------

function copiarTexto(id) {

    navigator.clipboard.writeText(

        document.getElementById(id).innerText

    );

}

// ----------------------------
// Inicialização
// ----------------------------

document.addEventListener("DOMContentLoaded", () => {

    initCodeMirror();

});