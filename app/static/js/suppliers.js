// ============================================
// HERMES - Modulo de Proveedores
// ============================================

let _proveedoresCache = [];


// ---------- LISTADO ----------
async function cargarProveedores() {
    const grid = document.getElementById('proveedores-grid');
    if (!grid) return;

    try {
        const resp = await fetch('/api/suppliers/', { credentials: 'same-origin' });
        if (resp.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
        if (!resp.ok) throw new Error('Error al obtener proveedores');
        const data = await resp.json();
        _proveedoresCache = data.proveedores || [];
        renderProveedores(_proveedoresCache);
    } catch (err) {
        grid.innerHTML = '<p class="error">No se pudieron cargar los proveedores.</p>';
        console.error(err);
    }
}

function renderProveedores(proveedores) {
    const grid = document.getElementById('proveedores-grid');
    if (!grid) return;

    if (!proveedores.length) {
        grid.innerHTML = '<p class="cargando">No hay proveedores registrados.</p>';
        return;
    }

    grid.innerHTML = proveedores.map(p => {
        const saldo = p.saldo_pendiente > 0
            ? `<span style="color: #e74c3c; font-weight: 700;">$${p.saldo_pendiente.toFixed(2)}</span>`
            : `<span style="color: #2ecc71;">$0.00</span>`;

        return `
            <a href="/suppliers/${p.id}" class="proveedor-card">
                <h3>${p.nombre}</h3>
                <div class="saldo">Saldo: ${saldo}</div>
                <div class="contacto">${p.telefono || p.email || ''}</div>
            </a>
        `;
    }).join('');
}

function filtrarProveedores(texto) {
    const t = texto.trim().toLowerCase();
    const filtrados = !t
        ? _proveedoresCache
        : _proveedoresCache.filter(p =>
            (p.nombre || '').toLowerCase().includes(t) ||
            (p.contacto || '').toLowerCase().includes(t) ||
            (p.email || '').toLowerCase().includes(t)
        );
    renderProveedores(filtrados);
}


// ---------- FORMULARIO (crear / editar) ----------
async function precargarFormulario(id) {
    try {
        const resp = await fetch(`/api/suppliers/${id}`, { credentials: 'same-origin' });
        if (!resp.ok) throw new Error('No se pudo cargar el proveedor');
        const data = await resp.json();
        const p = data.proveedor || data;

        document.getElementById('nombre').value = p.nombre || '';
        document.getElementById('contacto').value = p.contacto || '';
        document.getElementById('telefono').value = p.telefono || '';
        document.getElementById('email').value = p.email || '';
        document.getElementById('direccion').value = p.direccion || '';
        const saldoEl = document.getElementById('saldo_pendiente');
        if (saldoEl) saldoEl.value = p.saldo_pendiente || 0;
    } catch (err) {
        console.error(err);
        alert('No se pudo cargar el proveedor');
    }
}

async function guardarProveedor(modo, id) {
    const datos = {
        nombre: document.getElementById('nombre').value.trim(),
        contacto: document.getElementById('contacto').value.trim(),
        telefono: document.getElementById('telefono').value.trim(),
        email: document.getElementById('email').value.trim(),
        direccion: document.getElementById('direccion').value.trim(),
        saldo_pendiente: parseFloat(document.getElementById('saldo_pendiente')?.value || 0),
    };

    if (!datos.nombre || !datos.email) {
        alert('Nombre y email son obligatorios');
        return;
    }

    const url = modo === 'editar' ? `/api/suppliers/${id}` : '/api/suppliers/';
    const method = modo === 'editar' ? 'PUT' : 'POST';

    try {
        const resp = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(datos)
        });

        const data = await resp.json();

        if (data.success) {
            window.location.href = '/suppliers/';
        } else {
            alert('Error: ' + (data.error || 'No se pudo guardar'));
        }
    } catch (err) {
        console.error(err);
        alert('Error de conexion');
    }
}


// ---------- ELIMINAR ----------
async function eliminarProveedor(id, nombre) {
    if (!confirm(`Eliminar proveedor "${nombre}"?`)) return;

    try {
        const resp = await fetch(`/api/suppliers/${id}`, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        const data = await resp.json();

        if (data.success) {
            alert(data.message || 'Proveedor eliminado');
            window.location.href = '/suppliers/';
        } else {
            alert('Error: ' + (data.error || 'No se pudo eliminar'));
        }
    } catch (err) {
        console.error(err);
        alert('Error de conexion');
    }
}
