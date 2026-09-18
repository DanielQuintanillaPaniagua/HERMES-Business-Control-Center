// ============================================
// HERMES AI - lógica del chat
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chatInput');
    const btnEnviar = document.getElementById('btnEnviarChat');
    const contenedor = document.getElementById('chatMensajes');
    const sugerencias = document.getElementById('chatSugerencias');

    function enviar(texto) {
        const mensaje = (texto ?? input.value).trim();
        if (!mensaje) return;

        agregarMensaje(mensaje, 'usuario');
        input.value = '';
        sugerencias.style.display = 'none';
        enviarAlBackend(mensaje);
    }

    btnEnviar.addEventListener('click', () => enviar());
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') enviar();
    });

    sugerencias.querySelectorAll('.chip-sugerencia').forEach(chip => {
        chip.addEventListener('click', () => enviar(chip.textContent));
    });

    function agregarMensaje(texto, tipo, esError = false) {
        const div = document.createElement('div');
        div.className = `msg msg-${tipo === 'usuario' ? 'usuario' : 'ia'}${esError ? ' error' : ''}`;
        div.textContent = texto;
        contenedor.appendChild(div);
        contenedor.scrollTop = contenedor.scrollHeight;
        return div;
    }

    function mostrarEscribiendo() {
        const div = document.createElement('div');
        div.className = 'msg msg-ia typing-dots';
        div.id = 'indicadorEscribiendo';
        div.innerHTML = '<span></span><span></span><span></span>';
        contenedor.appendChild(div);
        contenedor.scrollTop = contenedor.scrollHeight;
    }

    function quitarEscribiendo() {
        document.getElementById('indicadorEscribiendo')?.remove();
    }

    async function enviarAlBackend(mensaje) {
        btnEnviar.disabled = true;
        mostrarEscribiendo();

        try {
            const resp = await fetch('/api/ia-hermes/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensaje })
            });
            const data = await resp.json();
            quitarEscribiendo();

            if (data.success) {
                agregarMensaje(data.respuesta, 'ia');
            } else {
                agregarMensaje(data.error || 'Ocurrió un error inesperado.', 'ia', true);
            }
        } catch (err) {
            quitarEscribiendo();
            agregarMensaje('No se pudo conectar con el servidor. Intenta de nuevo.', 'ia', true);
            console.error('Error en chat IA:', err);
        } finally {
            btnEnviar.disabled = false;
        }
    }
});