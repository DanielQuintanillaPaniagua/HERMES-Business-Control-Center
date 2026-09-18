// ============================================
// HERMES - lógica global (sidebar, perfil, notificaciones)
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    inicializarSidebarMovil();
    inicializarCambioFoto();
    cargarAvatarGuardado();
    cargarNotificaciones();
    inicializarBuscador();
});

// ---------- Sidebar móvil ----------
function inicializarSidebarMovil() {
    const btn = document.getElementById('btnToggleSidebar');
    const sidebar = document.getElementById('sidebar');
    if (!btn || !sidebar) return;

    btn.addEventListener('click', () => sidebar.classList.toggle('sidebar-open'));

    document.addEventListener('click', (e) => {
        if (window.innerWidth > 991) return;
        if (!sidebar.contains(e.target) && !btn.contains(e.target)) {
            sidebar.classList.remove('sidebar-open');
        }
    });
}

// ---------- Foto de perfil ----------
// NOTA: esto guarda la foto solo en este navegador (localStorage).
// Para que se vea igual en cualquier dispositivo, hace falta un endpoint
// en el backend (ej. POST /auth/profile/avatar) que la guarde en el servidor.
function inicializarCambioFoto() {
    const btnCambiar = document.getElementById('btnCambiarFoto');
    const input = document.getElementById('inputFoto');
    if (!btnCambiar || !input) return;

    btnCambiar.addEventListener('click', () => input.click());

    input.addEventListener('change', () => {
        const file = input.files[0];
        if (!file) return;

        if (file.size > 2 * 1024 * 1024) {
            alert('La imagen es muy pesada. Usa una menor a 2MB.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const base64 = e.target.result;
            document.getElementById('avatarPreview').src = base64;
            try {
                localStorage.setItem('hermes_avatar', base64);
            } catch (err) {
                console.warn('No se pudo guardar la foto localmente:', err);
            }
        };
        reader.readAsDataURL(file);
    });
}

function cargarAvatarGuardado() {
    const guardado = localStorage.getItem('hermes_avatar');
    const el = document.getElementById('avatarPreview');
    if (guardado && el) el.src = guardado;
}

// ---------- Notificaciones (reutiliza la API de alertas del dashboard) ----------
async function cargarNotificaciones() {
    const contenedor = document.getElementById('listaNotificaciones');
    const dot = document.getElementById('badgeNotifDot');
    if (!contenedor) return;

    try {
        const resp = await fetch('/api/dashboard/alerts');
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        const alertas = data.alerts || [];

        if (alertas.length === 0) {
            contenedor.innerHTML = '<h6 class="dropdown-header">Notificaciones</h6><div class="text-center text-muted py-3">Sin novedades 🎉</div>';
            if (dot) dot.style.display = 'none';
            return;
        }

        const iconos = { danger: 'bi-exclamation-circle-fill text-danger', warning: 'bi-exclamation-triangle-fill text-warning', info: 'bi-info-circle-fill text-info' };
        contenedor.innerHTML = '<h6 class="dropdown-header">Notificaciones</h6>' + alertas.map(a => `
            <a class="dropdown-item" href="${a.url || '#'}">
                <i class="bi ${iconos[a.tipo] || iconos.info} me-2"></i>${a.mensaje}
            </a>
        `).join('');
    } catch (err) {
        contenedor.innerHTML = '<h6 class="dropdown-header">Notificaciones</h6><div class="text-center text-muted py-3">No se pudieron cargar</div>';
        console.error('Error cargando notificaciones:', err);
    }
}

// ---------- Buscador (placeholder visual por ahora) ----------
function inicializarBuscador() {
    const input = document.getElementById('buscadorGlobal');
    if (!input) return;
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && input.value.trim()) {
            // TODO: cuando exista un endpoint de búsqueda global, conectar aquí.
            console.log('Buscar:', input.value.trim());
        }
    });
}

console.log('✅ HERMES: main.js cargado');