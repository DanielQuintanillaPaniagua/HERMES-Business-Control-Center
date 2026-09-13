/* ==========================================================================
   HERMES AI - lógica del chat
   - askHermesAI(pregunta) es el punto de integración con el backend Flask.
     Cuando el endpoint exista, reemplazar el bloque MOCK por el fetch real:

       const res = await fetch("/api/hermes-ai", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ pregunta })
       });
       const data = await res.json();
       return data;   // { respuesta: "...", tabla: {...} | null }

   - El backend debe devolver texto en lenguaje natural y, opcionalmente,
     una tabla de datos (por ejemplo pedidos atrasados) para renderizar.
   ========================================================================== */

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");


async function askHermesAI(pregunta) {
    await new Promise((r) => setTimeout(r, 700));

    if (/atrasad/i.test(pregunta)) {
        return {
            respuesta: "Tienes 7 pedidos atrasados. Estos son los más urgentes:",
            tabla: {
                headers: ["Pedido", "Cliente", "Días de retraso", "Total"],
                rows: [
                    ["#1021", "Distribuidora López", "4 días", "$1,290.00"],
                    ["#1023", "Supermercado El Sol", "3 días", "$2,340.00"],
                    ["#1045", "Tiendas Unidas", "2 días", "$950.00"]
                ]
            }
        };
    }

    if (/prove/i.test(pregunta)) {
        return { respuesta: "Actualmente se deben $8,420.00 a proveedores, repartidos entre 5 cuentas activas.", tabla: null };
    }

    return { respuesta: "Estoy consultando la base de datos del negocio para responder eso. (Respuesta de ejemplo mientras se conecta el backend.)", tabla: null };
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