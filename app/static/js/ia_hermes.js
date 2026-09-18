

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");


async function askHermesAI(pregunta) {
    try {
        const res = await fetch("/api/ai/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ pregunta: pregunta })
        });

        if (res.status === 401) {
            window.location.href = "/auth/login";
            return { respuesta: "Tu sesión ha expirado. Por favor inicia sesión de nuevo.", tabla: null };
        }

        const data = await res.json();

        if (data.success) {
            return {
                respuesta: data.respuesta,
                tabla: null  // Tu API no devuelve tablas, solo texto
            };
        } else {
            return {
                respuesta: "❌ " + (data.error || "Error al procesar la consulta."),
                tabla: null
            };
        }
    } catch (error) {
        console.error("Error al llamar a HERMES AI:", error);
        return {
            respuesta: "No pude conectarme con el servidor. Intenta de nuevo en unos segundos.",
            tabla: null
        };
    }
}
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendUserMessage(text) {
    const el = document.createElement("div");
    el.className = "msg from-user";
    el.innerHTML = `<div class="bubble"></div>`;
    el.querySelector(".bubble").textContent = text;
    chatMessages.appendChild(el);
    scrollToBottom();
}

function appendTypingIndicator() {
    const el = document.createElement("div");
    el.className = "msg from-ai";
    el.id = "typingIndicator";
    el.innerHTML = `
    <div class="ai-avatar">H</div>
    <div class="bubble">
      <span class="typing-dots"><span></span><span></span><span></span></span>
    </div>`;
    chatMessages.appendChild(el);
    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
}

function buildTableHTML(tabla) {
    if (!tabla) return "";
    const head = tabla.headers.map((h) => `<th>${h}</th>`).join("");
    const rows = tabla.rows
        .map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`)
        .join("");
    return `<div class="ai-table"><table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

function appendAIMessage({ respuesta, tabla }) {
    const el = document.createElement("div");
    el.className = "msg from-ai";
    el.innerHTML = `
    <div class="ai-avatar">H</div>
    <div>
      <div class="bubble">${respuesta}</div>
      ${buildTableHTML(tabla)}
    </div>`;
    chatMessages.appendChild(el);
    scrollToBottom();
}

async function handleSend(text) {
    const pregunta = (text ?? chatInput.value).trim();
    if (!pregunta) return;

    appendUserMessage(pregunta);
    chatInput.value = "";
    sendBtn.disabled = true;

    appendTypingIndicator();
    try {
        const data = await askHermesAI(pregunta);
        removeTypingIndicator();
        appendAIMessage(data);
    } catch (err) {
        removeTypingIndicator();
        appendAIMessage({ respuesta: "No pude conectarme con el servidor. Intenta de nuevo en unos segundos.", tabla: null });
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

sendBtn.addEventListener("click", () => handleSend());
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSend();
});


document.querySelectorAll(".quick-chip, .suggestion-card").forEach((el) => {
    el.addEventListener("click", () => handleSend(el.dataset.q));
});