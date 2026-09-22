// ============================================
// HELPERS DE FORMATO
// ============================================
function escaparHtml(valor) {
    return String(valor ?? '')
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function formatearPrecio(valor) {
    return '$' + Number(valor || 0).toLocaleString('en-US', {
        minimumFractionDigits: 2, maximumFractionDigits: 2
    });
}

// estado: pendiente=naranja, completado=verde, atrasado=rojo, cancelado=gris
function badgeEstado(estado) {
    const clases = {
        'Pendiente': 'badge-pendiente',
        'Completado': 'badge-completado',
        'Atrasado': 'badge-atrasado',
        'Cancelado': 'badge-cancelado'
    };
    const clase = clases[estado] || 'badge-pendiente';
    return `<span class="${clase}">${escaparHtml(estado)}</span>`;
}

function formatearFecha(fecha) {
    if (!fecha) return '—';
    const iso = /(Z|[+-]\d\d:\d\d)$/.test(fecha) ? fecha : fecha + 'Z';
    return new Date(iso).toLocaleDateString('es-ES', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

// ============================================
// SELECTORES DINÁMICOS: CLIENTES Y PRODUCTOS
// ============================================
async function cargarClientes() {
    const select = document.getElementById('cliente_id');
    if (!select) return;

    try {
        const res = await fetch('/api/clients/', { credentials: 'same-origin' });
        const data = await res.json();

        select.innerHTML = '<option value="">Selecciona un cliente</option>';

        if (data.success && data.clientes.length > 0) {
            data.clientes.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = c.nombre;
                select.appendChild(opt);
            });
        } else {
            select.innerHTML = '<option value="">No hay clientes registrados</option>';
        }
    } catch (error) {
        console.error('Error al cargar clientes:', error);
        select.innerHTML = '<option value="">Error al cargar clientes</option>';
    }
}

async function cargarProductosSelect() {
    const select = document.getElementById('producto_id');
    if (!select) return;

    try {
        const res = await fetch('/api/products/', { credentials: 'same-origin' });
        const data = await res.json();

        select.innerHTML = '<option value="">Selecciona un producto</option>';

        if (data.success && data.productos.length > 0) {
            data.productos.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = `${p.nombre} (${formatearPrecio(p.precio)} · Stock: ${p.stock})`;
                select.appendChild(opt);
            });
        } else {
            select.innerHTML = '<option value="">No hay productos registrados</option>';
        }
    } catch (error) {
        console.error('Error al cargar productos:', error);
        select.innerHTML = '<option value="">Error al cargar productos</option>';
    }
}

// ============================================
// LISTADO
// ============================================
async function cargarPedidos() {
    const contenedor = document.getElementById('lista-pedidos');
    if (!contenedor) return;

    try {
        const response = await fetch('/api/orders/', { credentials: 'same-origin' });

        if (response.status === 401) {
            window.location.href = '/auth/login';
            return;
        }

        const data = await response.json();

        if (!data.success) {
            contenedor.innerHTML = '<p class="text-danger p-3">Error al cargar pedidos</p>';
            return;
        }

        if (data.pedidos.length === 0) {
            contenedor.innerHTML = `
                <div class="estado-vacio">
                    <i class="bi bi-cart-check"></i>
                    <h4>No hay pedidos registrados</h4>
                    <p>Empieza creando tu primer pedido</p>
                    <a href="/orders/new" class="btn-gold">
                        <i class="bi bi-plus-circle"></i> Crear primer pedido
                    </a>
                </div>`;
            return;
        }

        let html = `
            <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead>
                    <tr>
                        <th>#</th><th>Cliente</th><th>Producto</th><th>Cantidad</th>
                        <th>Total</th><th>Estado</th><th>Fecha</th>
                        <th class="text-end">Acciones</th>
                    </tr>
                </thead>
                <tbody>`;

        data.pedidos.forEach(p => {
            html += `
                <tr>
                    <td>${p.id}</td>
                    <td>${escaparHtml(p.cliente_nombre) || '—'}</td>
                    <td>${escaparHtml(p.producto_nombre) || '—'}</td>
                    <td>${p.cantidad}</td>
                    <td>${formatearPrecio(p.total)}</td>
                    <td>${badgeEstado(p.estado)}</td>
                    <td>${formatearFecha(p.created_at)}</td>
                    <td class="text-end">
                        <a href="/orders/${p.id}" class="btn btn-sm btn-outline-primary" title="Ver">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="/orders/${p.id}/edit" class="btn btn-sm btn-outline-warning" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar" title="Eliminar"
                                data-id="${p.id}" data-nombre="Pedido #${p.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>`;
        });

        html += '</tbody></table></div>';
        contenedor.innerHTML = html;

    } catch (error) {
        console.error('Error al cargar pedidos:', error);
        contenedor.innerHTML = '<p class="text-danger p-3">Error de conexión</p>';
    }
}

// ============================================
// API: UNO / CREAR / ACTUALIZAR / ELIMINAR
// ============================================
async function cargarPedido(id) {
    try {
        const response = await fetch(`/api/orders/${id}`, { credentials: 'same-origin' });
        const data = await response.json();
        return data.success ? data.pedido : null;
    } catch (error) {
        console.error('Error al cargar pedido:', error);
        return null;
    }
}

async function enviarPedido(url, metodo, datos) {
    try {
        const response = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(datos)
        });
        return await response.json();
    } catch (error) {
        console.error('Error al guardar pedido:', error);
        return { success: false, error: 'Error de conexión' };
    }
}

const crearPedido = (datos) => enviarPedido('/api/orders/', 'POST', datos);
const actualizarPedido = (id, datos) => enviarPedido(`/api/orders/${id}`, 'PUT', datos);

async function eliminarPedido(id, nombre, volverALista = false) {
    if (!confirm(`¿Eliminar el "${nombre}"?`)) return;

    try {
        const response = await fetch(`/api/orders/${id}`, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            if (volverALista) {
                window.location.href = '/orders/';
            } else {
                cargarPedidos();
            }
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error de conexión');
    }
}

// ============================================
// FORMULARIO (crear / editar)
// ============================================
async function guardarFormularioPedido(event, pedidoId = null) {
    event.preventDefault();

    const clienteId = document.getElementById('cliente_id').value;
    const productoId = document.getElementById('producto_id').value;
    const cantidad = parseInt(document.getElementById('cantidad').value, 10);

    if (!clienteId || !productoId) {
        alert('Debes seleccionar un cliente y un producto');
        return;
    }

    if (Number.isNaN(cantidad) || cantidad <= 0) {
        alert('La cantidad debe ser un número mayor a 0');
        return;
    }

    const datos = {
        cliente_id: clienteId,
        producto_id: productoId,
        cantidad: cantidad,
        notas: document.getElementById('notas').value.trim(),
        estado: document.getElementById('estado')?.value || 'Pendiente'
    };

    const resultado = pedidoId
        ? await actualizarPedido(pedidoId, datos)
        : await crearPedido(datos);

    if (resultado.success) {
        window.location.href = '/orders/';
    } else {
        alert('Error: ' + resultado.error);
    }
}

async function cargarDatosFormularioPedido(pedidoId) {
    const pedido = await cargarPedido(pedidoId);
    if (!pedido) return;

    // Espera a que los selects terminen de poblarse antes de fijar su valor
    await Promise.all([cargarClientes(), cargarProductosSelect()]);

    document.getElementById('cliente_id').value = pedido.cliente_id ?? '';
    document.getElementById('producto_id').value = pedido.producto_id ?? '';
    document.getElementById('cantidad').value = pedido.cantidad ?? 1;
    document.getElementById('notas').value = pedido.notas || '';
    const estadoSelect = document.getElementById('estado');
    if (estadoSelect) estadoSelect.value = pedido.estado || 'Pendiente';
}

// ============================================
// DETALLE
// ============================================
async function mostrarDetallePedido(pedidoId) {
    const contenedor = document.getElementById('detalle-pedido-card');
    const pedido = await cargarPedido(pedidoId);

    if (!pedido) {
        contenedor.innerHTML = `
            <div class="detalle-body text-center py-5">
                <i class="bi bi-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
                <h4 class="mt-3">Pedido no encontrado</h4>
                <a href="/orders/" class="btn-gold mt-3">Volver a la lista</a>
            </div>`;
        return;
    }

    contenedor.innerHTML = `
        <div class="detalle-header">
            <h4><i class="bi bi-cart-check"></i> Pedido #${pedido.id}</h4>
            ${badgeEstado(pedido.estado)}
        </div>
        <div class="detalle-body">
            <div class="detalle-fila"><span class="label">Cliente</span><span class="valor">${escaparHtml(pedido.cliente_nombre) || '—'}</span></div>
            <div class="detalle-fila"><span class="label">Producto</span><span class="valor">${escaparHtml(pedido.producto_nombre) || '—'}</span></div>
            <div class="detalle-fila"><span class="label">Cantidad</span><span class="valor">${pedido.cantidad}</span></div>
            <div class="detalle-fila"><span class="label">Precio unitario</span><span class="valor">${formatearPrecio(pedido.precio_unitario)}</span></div>
            <div class="detalle-fila"><span class="label">Total</span><span class="valor"><strong>${formatearPrecio(pedido.total)}</strong></span></div>
            <div class="detalle-fila"><span class="label">Notas</span><span class="valor">${escaparHtml(pedido.notas) || '—'}</span></div>
            <div class="detalle-fila"><span class="label">Fecha de registro</span><span class="valor">${formatearFecha(pedido.created_at)}</span></div>
        </div>
        <div class="detalle-footer">
            <button type="button" class="btn btn-outline-danger btn-eliminar-detalle"
                    data-id="${pedido.id}" data-nombre="Pedido #${pedido.id}">
                <i class="bi bi-trash"></i> Eliminar
            </button>
            <a href="/orders/${pedido.id}/edit" class="btn-gold">
                <i class="bi bi-pencil"></i> Editar
            </a>
        </div>`;
}

// ============================================
// INICIALIZACIÓN AUTOMÁTICA
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Listado
    const lista = document.getElementById('lista-pedidos');
    if (lista) {
        cargarPedidos();
        lista.addEventListener('click', (e) => {
            const boton = e.target.closest('.btn-eliminar');
            if (boton) eliminarPedido(boton.dataset.id, boton.dataset.nombre);
        });
    }

    // Formulario (crear o editar)
    const form = document.getElementById('form-pedido');
    if (form) {
        const pedidoId = form.dataset.pedidoId || null;
        form.addEventListener('submit', (e) => guardarFormularioPedido(e, pedidoId));

        if (pedidoId) {
            cargarDatosFormularioPedido(pedidoId);
        } else {
            cargarClientes();
            cargarProductosSelect();
        }
    }

    // Detalle
    const detalle = document.getElementById('detalle-pedido-card');
    if (detalle) {
        mostrarDetallePedido(detalle.dataset.pedidoId);
        detalle.addEventListener('click', (e) => {
            const boton = e.target.closest('.btn-eliminar-detalle');
            if (boton) eliminarPedido(boton.dataset.id, boton.dataset.nombre, true);
        });
    }
});