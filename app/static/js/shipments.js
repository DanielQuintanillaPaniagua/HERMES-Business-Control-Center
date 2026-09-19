
function escaparHtml(valor) {
    return String(valor ?? '')
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function capitalizar(texto) {
    const t = String(texto ?? '').trim();
    return t.charAt(0).toUpperCase() + t.slice(1);
}

function formatearPrecio(valor) {
    return '$' + Number(valor || 0).toLocaleString('en-US', {
        minimumFractionDigits: 2, maximumFractionDigits: 2
    });
}

function formatearFecha(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('es-ES', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });
}

function formatearFechaHora(iso) {
    if (!iso) return '—';
    const utc = /(Z|[+-]\d\d:\d\d)$/.test(iso) ? iso : iso + 'Z';
    return new Date(utc).toLocaleDateString('es-ES', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function aInputFecha(iso) {
    return iso ? iso.slice(0, 10) : '';
}

function badgeEstado(estado) {
    const e = String(estado || '').toLowerCase().trim();
    let clase = 'badge-otro';
    if (e === 'preparando') clase = 'badge-preparando';
    else if (['en camino', 'en tránsito', 'en transito', 'enviado'].includes(e)) clase = 'badge-camino';
    else if (e === 'entregado') clase = 'badge-entregado';
    else if (['retrasado', 'atrasado'].includes(e)) clase = 'badge-retrasado';
    return `<span class="badge-envio ${clase}">${escaparHtml(capitalizar(estado))}</span>`;
}

function estaVencido(envio) {
    const e = String(envio.estado || '').toLowerCase().trim();
    if (!envio.fecha_entrega_estimada || e === 'entregado' || e === 'cancelado') return false;
    const hoy = new Date(new Date().toDateString());
    return new Date(envio.fecha_entrega_estimada) < hoy;
}

function fechaEntregaHtml(envio) {
    const f = formatearFecha(envio.fecha_entrega_estimada);
    return estaVencido(envio)
        ? `<span class="text-danger" title="Fecha de entrega vencida"><i class="bi bi-exclamation-triangle"></i> ${f}</span>`
        : f;
}

async function cargarEnvios() {
    const contenedor = document.getElementById('lista-envios');
    if (!contenedor) return;

    try {
        const response = await fetch('/api/shipments/', { credentials: 'same-origin' });

        if (response.status === 401) {
            window.location.href = '/auth/login';
            return;
        }

        const data = await response.json();

        if (!data.success) {
            contenedor.innerHTML = '<p class="text-danger p-3">Error al cargar envíos</p>';
            return;
        }

        const total = document.getElementById('total-envios');
        if (total) total.textContent = `${data.total} envío(s) registrados`;

        if (data.envios.length === 0) {
            contenedor.innerHTML = `
                <div class="estado-vacio">
                    <i class="bi bi-send"></i>
                    <h4>No hay envíos registrados</h4>
                    <p>Empieza creando tu primer envío</p>
                    <a href="/shipments/new" class="btn-gold">
                        <i class="bi bi-plus-circle"></i> Crear primer envío
                    </a>
                </div>`;
            return;
        }

        let html = `
            <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead>
                    <tr>
                        <th>#</th><th>Pedido</th><th>Guía</th><th>Transportista</th>
                        <th>Ciudad</th><th>Entrega estimada</th><th>Estado</th>
                        <th class="text-end">Acciones</th>
                    </tr>
                </thead>
                <tbody>`;

        data.envios.forEach(e => {
            html += `
                <tr>
                    <td>${e.id}</td>
                    <td>#${e.pedido_id}</td>
                    <td><strong>${escaparHtml(e.numero_guia) || '—'}</strong></td>
                    <td>${escaparHtml(e.transportista) || '—'}</td>
                    <td>${escaparHtml(e.ciudad) || '—'}</td>
                    <td>${fechaEntregaHtml(e)}</td>
                    <td>${badgeEstado(e.estado)}</td>
                    <td class="text-end">
                        <a href="/shipments/${e.id}" class="btn btn-sm btn-outline-primary" title="Ver">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="/shipments/${e.id}/edit" class="btn btn-sm btn-outline-warning" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar" title="Eliminar"
                                data-id="${e.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>`;
        });

        html += '</tbody></table></div>';
        contenedor.innerHTML = html;

    } catch (error) {
        console.error('Error al cargar envíos:', error);
        contenedor.innerHTML = '<p class="text-danger p-3">Error de conexión</p>';
    }
}

async function cargarEnvio(id) {
    try {
        const response = await fetch(`/api/shipments/${id}`, { credentials: 'same-origin' });
        const data = await response.json();
        return data.success ? data.envio : null;
    } catch (error) {
        console.error('Error al cargar envío:', error);
        return null;
    }
}

async function enviarEnvio(url, metodo, datos) {
    try {
        const response = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(datos)
        });
        return await response.json();
    } catch (error) {
        console.error('Error al guardar envío:', error);
        return { success: false, error: 'Error de conexión' };
    }
}

const crearEnvio = (datos) => enviarEnvio('/api/shipments/', 'POST', datos);
const actualizarEnvio = (id, datos) => enviarEnvio(`/api/shipments/${id}`, 'PUT', datos);

async function eliminarEnvio(id, volverALista = false) {
    if (!confirm(`¿Eliminar el envío #${id}?`)) return;

    try {
        const response = await fetch(`/api/shipments/${id}`, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            if (volverALista) {
                window.location.href = '/shipments/';
            } else {
                cargarEnvios();
            }
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error de conexión');
    }
}

function etiquetaPedido(p) {
    const partes = [`Pedido #${p.id}`];
    const cliente = p.cliente_nombre || p.cliente;
    if (typeof cliente === 'string' && cliente) partes.push(cliente);
    if (p.total !== undefined && p.total !== null) partes.push(formatearPrecio(p.total));
    return partes.join(' — ');
}

async function cargarPedidos(select) {
    try {
        const response = await fetch('/api/orders/', { credentials: 'same-origin' });
        const data = await response.json();
        if (!data.success) return;

        if (data.pedidos.length === 0) {
            select.options[0].textContent = 'No hay pedidos registrados: crea uno primero';
            return;
        }

        data.pedidos.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = etiquetaPedido(p);
            select.appendChild(opt);
        });
    } catch (error) {
        console.error('Error al cargar pedidos:', error);
    }
}

// FORMULARIO (crear / editar)
async function guardarFormulario(event, envioId = null) {
    event.preventDefault();

    const datos = {
        direccion_envio: document.getElementById('direccion_envio').value.trim(),
        ciudad: document.getElementById('ciudad').value.trim(),
        transportista: document.getElementById('transportista').value.trim(),
        numero_guia: document.getElementById('numero_guia').value.trim().toUpperCase(),
        fecha_entrega_estimada: document.getElementById('fecha_entrega_estimada').value
    };

    let resultado;
    if (envioId) {
        datos.estado = document.getElementById('estado').value;
        datos.fecha_envio = document.getElementById('fecha_envio').value;
        resultado = await actualizarEnvio(envioId, datos);
    } else {
        datos.pedido_id = parseInt(document.getElementById('pedido_id').value, 10);
        resultado = await crearEnvio(datos);
    }

    if (resultado.success) {
        window.location.href = '/shipments/';
    } else {
        alert('Error: ' + resultado.error);
    }
}

function seleccionarEstado(select, valor) {
    const buscado = String(valor || '').toLowerCase().trim();
    for (const opt of select.options) {
        if (opt.value.toLowerCase() === buscado) {
            select.value = opt.value;
            return;
        }
    }
}

async function cargarDatosFormulario(envioId) {
    const selectPedido = document.getElementById('pedido_id');
    await cargarPedidos(selectPedido);

    const envio = await cargarEnvio(envioId);
    if (!envio) {
        alert('No se pudo cargar el envío');
        return;
    }

    selectPedido.value = envio.pedido_id;
    selectPedido.disabled = true;

    document.getElementById('direccion_envio').value = envio.direccion_envio || '';
    document.getElementById('ciudad').value = envio.ciudad || '';
    document.getElementById('transportista').value = envio.transportista || '';
    document.getElementById('numero_guia').value = envio.numero_guia || '';
    document.getElementById('fecha_entrega_estimada').value = aInputFecha(envio.fecha_entrega_estimada);
    document.getElementById('fecha_envio').value = aInputFecha(envio.fecha_envio);
    seleccionarEstado(document.getElementById('estado'), envio.estado);
}

async function mostrarDetalle(envioId) {
    const contenedor = document.getElementById('detalle-envio-card');
    const envio = await cargarEnvio(envioId);

    if (!envio) {
        contenedor.innerHTML = `
            <div class="detalle-body text-center py-5">
                <i class="bi bi-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
                <h4 class="mt-3">Envío no encontrado</h4>
                <a href="/shipments/" class="btn-gold mt-3">Volver a la lista</a>
            </div>`;
        return;
    }

    contenedor.innerHTML = `
        <div class="detalle-header">
            <h4><i class="bi bi-send"></i> Envío #${envio.id}</h4>
            ${badgeEstado(envio.estado)}
        </div>
        <div class="detalle-body">
            <div class="detalle-fila"><span class="label">Pedido</span><span class="valor">#${envio.pedido_id}</span></div>
            <div class="detalle-fila"><span class="label">Nº de guía</span><span class="valor"><strong>${escaparHtml(envio.numero_guia) || '—'}</strong></span></div>
            <div class="detalle-fila"><span class="label">Transportista</span><span class="valor">${escaparHtml(envio.transportista) || '—'}</span></div>
            <div class="detalle-fila"><span class="label">Dirección</span><span class="valor">${escaparHtml(envio.direccion_envio)}</span></div>
            <div class="detalle-fila"><span class="label">Ciudad</span><span class="valor">${escaparHtml(envio.ciudad) || '—'}</span></div>
            <div class="detalle-fila"><span class="label">Fecha de envío</span><span class="valor">${formatearFecha(envio.fecha_envio)}</span></div>
            <div class="detalle-fila"><span class="label">Entrega estimada</span><span class="valor">${fechaEntregaHtml(envio)}</span></div>
            <div class="detalle-fila"><span class="label">Fecha de registro</span><span class="valor">${formatearFechaHora(envio.created_at)}</span></div>
        </div>
        <div class="detalle-footer">
            <button type="button" class="btn btn-outline-danger btn-eliminar-detalle" data-id="${envio.id}">
                <i class="bi bi-trash"></i> Eliminar
            </button>
            <a href="/shipments/${envio.id}/edit" class="btn-gold">
                <i class="bi bi-pencil"></i> Editar
            </a>
        </div>`;
}

document.addEventListener('DOMContentLoaded', () => {
    const lista = document.getElementById('lista-envios');
    if (lista) {
        cargarEnvios();
        lista.addEventListener('click', (e) => {
            const boton = e.target.closest('.btn-eliminar');
            if (boton) eliminarEnvio(boton.dataset.id);
        });
    }

    // Formulario (crear o editar)
    const form = document.getElementById('form-envio');
    if (form) {
        const envioId = form.dataset.envioId || null;
        form.addEventListener('submit', (e) => guardarFormulario(e, envioId));
        if (envioId) {
            cargarDatosFormulario(envioId);
        } else {
            cargarPedidos(document.getElementById('pedido_id'));
        }
    }

    // Detalle
    const detalle = document.getElementById('detalle-envio-card');
    if (detalle) {
        mostrarDetalle(detalle.dataset.envioId);
        detalle.addEventListener('click', (e) => {
            const boton = e.target.closest('.btn-eliminar-detalle');
            if (boton) eliminarEnvio(boton.dataset.id, true);
        });
    }
});