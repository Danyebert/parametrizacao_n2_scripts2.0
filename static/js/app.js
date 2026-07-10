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

    inicializarGeradorIdentificador();

    document
        .getElementById("pesquisaScripts")
        ?.addEventListener("keyup", pesquisarScripts);

    document
        .getElementById("filtroBanco")
        ?.addEventListener("change", filtrarBanco);

});

// ===========================================
// Gerador de Identificador
// ===========================================

const IDENTIFICADOR_HIST_KEY =
    "parametrizacao_n2_identificador_historico";


function getIdentificadorElement(id) {
    return document.getElementById(id);
}


function carregarHistoricoIdentificador() {
    try {
        const salvo = localStorage.getItem(IDENTIFICADOR_HIST_KEY);
        const historico = salvo ? JSON.parse(salvo) : [];

        return Array.isArray(historico) ? historico : [];
    } catch (erro) {
        console.error(
            "Erro ao carregar histórico de identificadores:",
            erro
        );

        return [];
    }
}


function salvarHistoricoIdentificador(historico) {
    localStorage.setItem(
        IDENTIFICADOR_HIST_KEY,
        JSON.stringify(historico)
    );
}


function escaparHtmlIdentificador(valor) {
    return String(valor ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function mostrarToastIdentificador(
    mensagem,
    tipo = "success"
) {
    let toast =
        getIdentificadorElement("identificadorToast");

    if (!toast) {
        toast = document.createElement("div");
        toast.id = "identificadorToast";
        toast.className = "identificador-toast";

        document.body.appendChild(toast);
    }

    toast.className =
        `identificador-toast show ${tipo}`;

    toast.innerHTML = `
        <i class="bi ${
            tipo === "danger"
                ? "bi-exclamation-triangle"
                : "bi-check-circle"
        }"></i>

        <span>
            ${escaparHtmlIdentificador(mensagem)}
        </span>
    `;

    clearTimeout(window.identificadorToastTimer);

    window.identificadorToastTimer =
        setTimeout(() => {
            toast.classList.remove("show");
        }, 2200);
}


async function copiarTextoIdentificador(
    texto,
    mensagem = "Copiado com sucesso!"
) {
    if (!texto) {
        mostrarToastIdentificador(
            "Não há conteúdo para copiar.",
            "danger"
        );

        return;
    }

    try {
        await navigator.clipboard.writeText(texto);

        mostrarToastIdentificador(mensagem);
    } catch (erro) {
        console.error("Erro ao copiar:", erro);

        mostrarToastIdentificador(
            "Não foi possível copiar.",
            "danger"
        );
    }
}


function atualizarMetricasIdentificador() {
    const historico =
        carregarHistoricoIdentificador();

    const hoje =
        new Date().toLocaleDateString("pt-BR");

    const total =
        getIdentificadorElement("metricTotalGerados");

    const hojeEl =
        getIdentificadorElement("metricGeradosHoje");

    const historicoEl =
        getIdentificadorElement("metricHistorico");

    const ultimo =
        getIdentificadorElement("metricUltimo");

    if (total) {
        total.textContent = historico.length;
    }

    if (hojeEl) {
        hojeEl.textContent =
            historico.filter(
                item => item.data === hoje
            ).length;
    }

    if (historicoEl) {
        historicoEl.textContent = historico.length;
    }

    if (ultimo) {
        ultimo.textContent =
            historico[0]?.identificador || "Nenhum";
    }
}


function renderHistoricoIdentificador() {
    const lista =
        getIdentificadorElement(
            "historicoIdentificadores"
        );

    if (!lista) {
        return;
    }

    const historico =
        carregarHistoricoIdentificador();

    if (!historico.length) {
        lista.innerHTML = `
            <div class="identificador-empty">
                <i class="bi bi-clock-history"></i>

                <h6>
                    Nenhum identificador gerado
                </h6>

                <p>
                    Os resultados aparecerão aqui
                    automaticamente.
                </p>
            </div>
        `;

        atualizarMetricasIdentificador();

        return;
    }

    lista.innerHTML =
        historico.map((item, indice) => `
            <article class="identificador-history-item">

                <div class="identificador-history-main">

                    <div class="identificador-history-number">
                        ${
                            escaparHtmlIdentificador(
                                item.numero || "Sem número"
                            )
                        }
                    </div>

                    <div class="identificador-history-value">
                        ${
                            escaparHtmlIdentificador(
                                item.identificador || ""
                            )
                        }
                    </div>

                    <div class="identificador-history-meta">

                        <span>
                            <i class="bi bi-calendar3"></i>

                            ${
                                escaparHtmlIdentificador(
                                    item.data || ""
                                )
                            }
                        </span>

                        <span>
                            <i class="bi bi-clock"></i>

                            ${
                                escaparHtmlIdentificador(
                                    item.hora || ""
                                )
                            }
                        </span>

                    </div>
                </div>

                <div class="identificador-history-actions">

                    <button
                        type="button"
                        class="btn btn-sm btn-outline-primary"
                        onclick="copiarHistoricoIdentificador(${indice})"
                        title="Copiar">

                        <i class="bi bi-clipboard"></i>
                    </button>

                    <button
                        type="button"
                        class="btn btn-sm btn-outline-danger"
                        onclick="removerHistoricoIdentificador(${indice})"
                        title="Remover">

                        <i class="bi bi-trash"></i>
                    </button>

                </div>
            </article>
        `).join("");

    atualizarMetricasIdentificador();
}


async function gerarIdentificador() {
    const linha =
        getIdentificadorElement(
            "linhaIdentificador"
        );

    const numero =
        getIdentificadorElement(
            "numeroIdentificador"
        );

    const identificador =
        getIdentificadorElement(
            "resultadoIdentificador"
        );

    const botao =
        getIdentificadorElement(
            "btnGerarIdentificador"
        );

    if (!linha || !numero || !identificador) {
        return;
    }

    const valor = linha.value.trim();

    if (!valor) {
        linha.focus();

        mostrarToastIdentificador(
            "Digite ou cole uma linha para gerar.",
            "danger"
        );

        return;
    }

    const textoOriginalBotao =
        botao?.innerHTML;

    if (botao) {
        botao.disabled = true;

        botao.innerHTML = `
            <span
                class="spinner-border spinner-border-sm">
            </span>

            Gerando...
        `;
    }

    try {
        const resposta =
            await fetch("/api/identificador", {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    linha: valor
                })
            });

        const dados =
            await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                dados.erro ||
                "Erro ao gerar identificador."
            );
        }

        numero.value =
            dados.numero || "";

        identificador.value =
            dados.identificador || "";

        if (!dados.identificador) {
            throw new Error(
                "Não foi possível identificar os dados informados."
            );
        }

        const agora = new Date();

        const historico =
            carregarHistoricoIdentificador();

        historico.unshift({
            numero:
                dados.numero || "",

            identificador:
                dados.identificador || "",

            entrada:
                valor,

            data:
                agora.toLocaleDateString("pt-BR"),

            hora:
                agora.toLocaleTimeString(
                    "pt-BR",
                    {
                        hour: "2-digit",
                        minute: "2-digit"
                    }
                )
        });

        salvarHistoricoIdentificador(
            historico.slice(0, 100)
        );

        renderHistoricoIdentificador();

        mostrarToastIdentificador(
            "Identificador gerado com sucesso!"
        );
    } catch (erro) {
        console.error(
            "Erro ao gerar identificador:",
            erro
        );

        mostrarToastIdentificador(
            erro.message ||
            "Erro ao gerar identificador.",
            "danger"
        );
    } finally {
        if (botao) {
            botao.disabled = false;

            botao.innerHTML =
                textoOriginalBotao;
        }
    }
}


function copiarNumeroIdentificador() {
    const valor =
        getIdentificadorElement(
            "numeroIdentificador"
        )?.value || "";

    copiarTextoIdentificador(
        valor,
        "Número copiado!"
    );
}


function copiarResultadoIdentificador() {
    const valor =
        getIdentificadorElement(
            "resultadoIdentificador"
        )?.value || "";

    copiarTextoIdentificador(
        valor,
        "Identificador copiado!"
    );
}


function copiarAmbosIdentificador() {
    const numero =
        getIdentificadorElement(
            "numeroIdentificador"
        )?.value || "";

    const identificador =
        getIdentificadorElement(
            "resultadoIdentificador"
        )?.value || "";

    if (!numero && !identificador) {
        mostrarToastIdentificador(
            "Gere um identificador primeiro.",
            "danger"
        );

        return;
    }

    copiarTextoIdentificador(
        `${numero};${identificador}`,
        "Número e identificador copiados!"
    );
}


function copiarHistoricoIdentificador(indice) {
    const item =
        carregarHistoricoIdentificador()[indice];

    if (!item) {
        return;
    }

    copiarTextoIdentificador(
        `${item.numero};${item.identificador}`,
        "Item do histórico copiado!"
    );
}


function removerHistoricoIdentificador(indice) {
    const historico =
        carregarHistoricoIdentificador();

    historico.splice(indice, 1);

    salvarHistoricoIdentificador(historico);

    renderHistoricoIdentificador();

    mostrarToastIdentificador(
        "Item removido do histórico."
    );
}


function limparHistoricoIdentificador() {
    const historico =
        carregarHistoricoIdentificador();

    if (!historico.length) {
        mostrarToastIdentificador(
            "O histórico já está vazio.",
            "danger"
        );

        return;
    }

    const confirmou =
        confirm(
            "Deseja limpar todo o histórico de identificadores?"
        );

    if (!confirmou) {
        return;
    }

    localStorage.removeItem(
        IDENTIFICADOR_HIST_KEY
    );

    renderHistoricoIdentificador();

    mostrarToastIdentificador(
        "Histórico limpo com sucesso!"
    );
}


function exportarHistoricoIdentificador() {
    const historico =
        carregarHistoricoIdentificador();

    if (!historico.length) {
        mostrarToastIdentificador(
            "Não há histórico para exportar.",
            "danger"
        );

        return;
    }

    const conteudo =
        historico
            .map(
                item =>
                    `${item.numero};${item.identificador}`
            )
            .join("\n");

    const blob =
        new Blob(
            [conteudo],
            {
                type:
                    "text/plain;charset=utf-8"
            }
        );

    const url =
        URL.createObjectURL(blob);

    const link =
        document.createElement("a");

    link.href = url;

    link.download =
        `historico_identificadores_${
            new Date()
                .toISOString()
                .slice(0, 10)
        }.txt`;

    document.body.appendChild(link);

    link.click();

    link.remove();

    URL.revokeObjectURL(url);

    mostrarToastIdentificador(
        "Histórico exportado com sucesso!"
    );
}


function limparFormularioIdentificador() {
    const linha =
        getIdentificadorElement(
            "linhaIdentificador"
        );

    const numero =
        getIdentificadorElement(
            "numeroIdentificador"
        );

    const identificador =
        getIdentificadorElement(
            "resultadoIdentificador"
        );

    if (linha) {
        linha.value = "";
    }

    if (numero) {
        numero.value = "";
    }

    if (identificador) {
        identificador.value = "";
    }

    atualizarContadorCaracteresIdentificador();

    linha?.focus();
}


function atualizarContadorCaracteresIdentificador() {
    const linha =
        getIdentificadorElement(
            "linhaIdentificador"
        );

    const contador =
        getIdentificadorElement(
            "contadorCaracteresIdentificador"
        );

    if (linha && contador) {
        contador.textContent =
            linha.value.length;
    }
}


function inicializarGeradorIdentificador() {
    const linha =
        getIdentificadorElement(
            "linhaIdentificador"
        );

    if (!linha) {
        return;
    }

    renderHistoricoIdentificador();

    atualizarContadorCaracteresIdentificador();

    linha.addEventListener(
        "input",
        atualizarContadorCaracteresIdentificador
    );

    linha.addEventListener(
        "keydown",
        evento => {
            if (
                (
                    evento.ctrlKey ||
                    evento.metaKey
                ) &&
                evento.key === "Enter"
            ) {
                evento.preventDefault();

                gerarIdentificador();
            }
        }
    );
}