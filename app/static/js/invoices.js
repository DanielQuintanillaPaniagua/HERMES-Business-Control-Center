let _facturasCache = [];


// ---------- LISTADO ----------
async function cargarFacturas() {
    const cont = document.getElementById('facturas-list');
    if (!cont) return;

    try {
        const resp = await fetch('/api/invoices/', { credentials: 'same-origin' });
        if (resp.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
        if (!resp.ok) throw new Error('Error al cargar facturas');

        const data = await resp.json();
        _facturasCache = data.facturas || [];
        renderFacturas(_facturasCache);
    } catch (err) {
        console.error(err);
        cont.innerHTML = '<p style="color: #e74c3c; text-align: center; padding: 40px;">Error al cargar facturas</p>';
    }
}

function renderFacturas(facturas) {
    const cont = document.getElementById('facturas-list');
    if (!cont) return;

    if (!facturas.length) {
        cont.innerHTML = `
            <div style="text-align: center; padding: 60px;">
                <i class="bi bi-file-earmark-text" style="font-size: 4rem; color: #d4af37; opacity: 0.5;"></i>
                <h4 style="color: #e0e0e0; margin-top: 20px;">No hay facturas registradas</h4>
                <p style="color: #888;">Crea tu primera factura</p>
                <a href="/invoices/new" class="btn-gold mt-3">Nueva factura</a>
            </div>
        `;
        return;
    }

    const filas = facturas.map(f => {
        let badgeClass = 'badge-pendiente';
        if (f.estado === 'Pagada') badgeClass = 'badge-pagada';
        else if (f.estado === 'Vencida') badgeClass = 'badge-vencida';

        const fechaEmision = f.fecha_emision ? f.fecha_emision.split('-').reverse().join('/') : '-';
        const fechaVencimiento = f.fecha_vencimiento ? f.fecha_vencimiento.split('-').reverse().join('/') : '-';

        return `
            <tr>
                <td><strong style="color: #d4af37;">${f.numero}</strong></td>
                <td>${f.cliente_nombre || '-'}</td>
                <td>${fechaEmision}</td>
                <td>${fechaVencimiento}</td>
                <td>${f.concepto || '-'}</td>
                <td>$${f.total.toFixed(2)}</td>
                <td><span class="${badgeClass}">${f.estado}</span></td>
                <td>
                    <a href="/invoices/${f.id}" class="btn-outline" style="padding: 6px 12px; font-size: 0.8rem;">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="/invoices/${f.id}/edit" class="btn-outline" style="padding: 6px 12px; font-size: 0.8rem;">
                        <i class="bi bi-pencil"></i>
                    </a>
                </td>
            </tr>
        `;
    }).join('');

    cont.innerHTML = `
        <div class="invoices-table">
            <table>
                <thead>
                    <tr>
                        <th># Factura</th>
                        <th>Cliente</th>
                        <th>Emision</th>
                        <th>Vencimiento</th>
                        <th>Concepto</th>
                        <th>Total (USD)</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>${filas}</tbody>
            </table>
        </div>
    `;
}

function filtrarFacturas(texto) {
    const t = texto.trim().toLowerCase();
    const filtrados = !t ? _facturasCache : _facturasCache.filter(f =>
        (f.numero || '').toLowerCase().includes(t) ||
        (f.cliente_nombre || '').toLowerCase().includes(t) ||
        (f.concepto || '').toLowerCase().includes(t)
    );
    renderFacturas(filtrados);
}


// ---------- FORMULARIO ----------
async function cargarClientesEnSelect() {
    const select = document.getElementById('client_id');
    if (!select) return;

    try {
        const resp = await fetch('/api/clients/', { credentials: 'same-origin' });
        const data = await resp.json();
        (data.clientes || []).forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.nombre;
            select.appendChild(opt);
        });
    } catch (err) { console.error(err); }
}

async function precargarFormulario(id) {
    try {
        const resp = await fetch(`/api/invoices/${id}`, { credentials: 'same-origin' });
        if (!resp.ok) throw new Error('No se pudo cargar');
        const data = await resp.json();
        const f = data.factura;

        document.getElementById('numero').value = f.numero || '';
        document.getElementById('client_id').value = f.client_id || '';
        document.getElementById('concepto').value = f.concepto || '';
        document.getElementById('fecha_emision').value = f.fecha_emision || '';
        document.getElementById('fecha_vencimiento').value = f.fecha_vencimiento || '';
        document.getElementById('total').value = f.total || 0;
        document.getElementById('estado').value = f.estado || 'Pendiente';
    } catch (err) {
        console.error(err);
        alert('No se pudo cargar la factura');
    }
}

async function guardarFactura(modo, id) {
    const datos = {
        numero: document.getElementById('numero').value.trim(),
        client_id: parseInt(document.getElementById('client_id').value),
        concepto: document.getElementById('concepto').value.trim(),
        fecha_emision: document.getElementById('fecha_emision').value,
        fecha_vencimiento: document.getElementById('fecha_vencimiento').value,
        total: parseFloat(document.getElementById('total').value || 0),
        estado: document.getElementById('estado').value
    };

    if (!datos.numero || !datos.client_id || !datos.concepto) {
        alert('Numero, cliente y concepto son obligatorios');
        return;
    }

    const url = modo === 'editar' ? `/api/invoices/${id}` : '/api/invoices/';
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
            window.location.href = '/invoices/';
        } else {
            alert('Error: ' + (data.error || 'No se pudo guardar'));
        }
    } catch (err) {
        console.error(err);
        alert('Error de conexion');
    }
}


// ---------- DETALLE ----------
async function cargarDetalleFactura(id) {
    const cont = document.getElementById('detalle-factura');
    try {
        const resp = await fetch(`/api/invoices/${id}`, { credentials: 'same-origin' });
        if (!resp.ok) throw new Error('No se encontro la factura');
        const data = await resp.json();
        const f = data.factura;

        let badgeClass = 'badge-pendiente';
        if (f.estado === 'Pagada') badgeClass = 'badge-pagada';
        else if (f.estado === 'Vencida') badgeClass = 'badge-vencida';

        const fechaEmision = f.fecha_emision ? f.fecha_emision.split('-').reverse().join('/') : '-';
        const fechaVencimiento = f.fecha_vencimiento ? f.fecha_vencimiento.split('-').reverse().join('/') : '-';

        cont.innerHTML = `
            <div class="detalle-card">
                <div class="detalle-header">
                    <h2>${f.numero}</h2>
                    <span class="${badgeClass}">${f.estado}</span>
                </div>
                <div class="detalle-body">
                    <div class="detalle-item">
                        <span class="label">Cliente</span>
                        <span class="valor">${f.cliente_nombre || '-'}</span>
                    </div>
                    <div class="detalle-item">
                        <span class="label">Concepto</span>
                        <span class="valor">${f.concepto || '-'}</span>
                    </div>
                    <div class="detalle-item">
                        <span class="label">Fecha de emision</span>
                        <span class="valor">${fechaEmision}</span>
                    </div>
                    <div class="detalle-item">
                        <span class="label">Fecha de vencimiento</span>
                        <span class="valor">${fechaVencimiento}</span>
                    </div>
                    <div class="detalle-item">
                        <span class="label">Total</span>
                        <span class="valor" style="color: #d4af37; font-weight: 700; font-size: 1.2rem;">$${f.total.toFixed(2)}</span>
                    </div>
                </div>
                <div class="detalle-footer">
    <a href="/api/invoices/${f.id}/download/json" class="btn-outline" download>
        <i class="bi bi-filetype-json"></i> JSON
    </a>
    <a href="/api/invoices/${f.id}/download/pdf" class="btn-outline" download>
        <i class="bi bi-filetype-pdf"></i> PDF
    </a>
    <a href="/invoices/${f.id}/edit" class="btn-gold">
        <i class="bi bi-pencil"></i> Editar
    </a>
</div>
            </div>
        `;
    } catch (err) {
        console.error(err);
        cont.innerHTML = '<p style="color: #e74c3c; text-align: center; padding: 40px;">No se pudo cargar la factura</p>';
    }
}


// ---------- INICIALIZACION ----------
document.addEventListener('DOMContentLoaded', () => {
    // Listado
    if (document.getElementById('facturas-list')) {
        cargarFacturas();
        const buscador = document.getElementById('buscador');
        if (buscador) {
            buscador.addEventListener('input', (e) => filtrarFacturas(e.target.value));
        }
    }

    // Formulario
    const form = document.getElementById('form-factura');
    if (form) {
        cargarClientesEnSelect().then(() => {
            const facturaId = form.dataset.facturaId;
            if (facturaId) {
                precargarFormulario(facturaId);
            }
        });

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const facturaId = form.dataset.facturaId;
            guardarFactura(facturaId ? 'editar' : 'crear', facturaId);
        });
    }
});