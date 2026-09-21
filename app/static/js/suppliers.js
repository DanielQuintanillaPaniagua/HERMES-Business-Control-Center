let _proveedoresCache = [];

/* ---------- LISTADO ---------- */

async function cargarProveedores() {
    const grid = document.getElementById('proveedores-grid');
    try {
        const resp = await fetch('/api/suppliers');
        if (!resp.ok) throw new Error('Error al obtener proveedores');
        _proveedoresCache = await resp.json();
        renderProveedores(_proveedoresCache);
    } catch (err) {
        grid.innerHTML = `<p class="error">No se pudieron cargar los proveedores.</p>`;
        console.error(err);
    }
}

function renderProveedores(proveedores) {
    const grid = document.getElementById('proveedores-grid');

    if (!proveedores.length) {
        grid.innerHTML = `<p class="cargando">No hay proveedores registrados.</p>`;
        return;
    }

    grid.innerHTML = proveedores.map(p => {
        const saldo = p.saldo_pendiente > 0
            ? `<span class="text-danger fw-bold">$${p.saldo_pendiente.toFixed(2)}</span>`
            : `<span class="text-success">$0.00</span>`;

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
            (p.contacto || '').toLowerCase().includes(t)
        );
    renderProveedores(filtrados);
}

/* ---------- FORMULARIO (crear / editar) ---------- */

async function precargarFormulario(id) {
    try {
        const resp = await fetch(`/api/suppliers/${id}`);
        if (!resp.ok) throw new Error('No se pudo cargar el proveedor');
        const p = await resp.json();
        document.getElementById('nombre').value = p.nombre || '';
        document.getElementById('contacto').value = p.contacto || '';
        document.getElementById('telefono').value = p.telefono || '';
        document.getElementById('email').value = p.email || '';
        document.getElementById('direccion').value = p.direccion || '';
    } catch (err) {
        alert('No se pudo cargar el proveedor para editar.');
        console.error(err);
    }
}

async function guardarProveedor(modo, id) {
    const payload = {
        nombre: document.getElementById('nombre').value.trim(),
        contacto: document.getElementById('contacto').value.trim(),
        telefono: document.getElementById('telefono').value.trim(),
        email: document.getElementById('email').value.trim(),
        direccion: document.getElementById('direccion').value.trim(),
    };

    if (!payload.nombre) {
        alert('El nombre es obligatorio.');
        return;
    }

    const url = modo === 'editar' ? `/api/suppliers/${id}` : '/api/suppliers';
    const method = modo === 'editar' ? 'PUT' : 'POST';

    try {
        const resp = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!resp.ok) throw new Error('Error al guardar el proveedor');
        const data = await resp.json();
        window.location.href = `/suppliers/${data.id}`;
    } catch (err) {
        alert('No se pudo guardar el proveedor.');
        console.error(err);
    }
}

/* ---------- ELIMINAR ---------- */

async function eliminarProveedor(id, nombre) {
    if (!confirm(`¿Eliminar al proveedor "${nombre}"? Esta acción no se puede deshacer.`)) {
        return;
    }
    try {
        const resp = await fetch(`/api/suppliers/${id}`, { method: 'DELETE' });
        if (!resp.ok) throw new Error('Error al eliminar el proveedor');
        window.location.href = '/suppliers';
    } catch (err) {
        alert('No se pudo eliminar el proveedor.');
        console.error(err);
    }
}