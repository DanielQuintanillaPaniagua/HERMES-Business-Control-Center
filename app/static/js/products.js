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

function formatearStock(stock) {
    const clase = stock < 10 ? 'text-danger' : 'text-success';
    return `<span class="${clase} fw-bold">${stock}</span>`;
}

function badgeEstado(estado) {
    return estado === 'Activo'
        ? '<span class="badge-activo">Activo</span>'
        : '<span class="badge-inactivo">Inactivo</span>';
}

// ============================================
// LISTADO
// ============================================
async function cargarProductos() {
    const contenedor = document.getElementById('lista-productos');
    if (!contenedor) return;

    try {
        const response = await fetch('/api/products/', { credentials: 'same-origin' });

        if (response.status === 401) {
            window.location.href = '/auth/login';
            return;
        }

        const data = await response.json();

        if (!data.success) {
            contenedor.innerHTML = '<p class="text-danger p-3">Error al cargar productos</p>';
            return;
        }

        if (data.productos.length === 0) {
            contenedor.innerHTML = `
                <div class="estado-vacio">
                    <i class="bi bi-box-seam"></i>
                    <h4>No hay productos registrados</h4>
                    <p>Empieza creando tu primer producto</p>
                    <a href="/products/new" class="btn-gold">
                        <i class="bi bi-plus-circle"></i> Crear primer producto
                    </a>
                </div>`;
            return;
        }

        let html = `
            <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead>
                    <tr>
                        <th>#</th><th>SKU</th><th>Nombre</th><th>Categoría</th>
                        <th>Precio</th><th>Stock</th><th>Estado</th>
                        <th class="text-end">Acciones</th>
                    </tr>
                </thead>
                <tbody>`;

        data.productos.forEach(p => {
            html += `
                <tr>
                    <td>${p.id}</td>
                    <td><strong>${escaparHtml(p.sku)}</strong></td>
                    <td>${escaparHtml(p.nombre)}</td>
                    <td>${escaparHtml(p.categoria) || '—'}</td>
                    <td>${formatearPrecio(p.precio)}</td>
                    <td>${formatearStock(p.stock)}</td>
                    <td>${badgeEstado(p.estado)}</td>
                    <td class="text-end">
                        <a href="/products/${p.id}" class="btn btn-sm btn-outline-primary" title="Ver">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="/products/${p.id}/edit" class="btn btn-sm btn-outline-warning" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar" title="Eliminar"
                                data-id="${p.id}" data-nombre="${escaparHtml(p.nombre)}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>`;
        });

        html += '</tbody></table></div>';
        contenedor.innerHTML = html;

    } catch (error) {
        console.error('Error al cargar productos:', error);
        contenedor.innerHTML = '<p class="text-danger p-3">Error de conexión</p>';
    }
}

// ============================================
// API: UNO / CREAR / ACTUALIZAR / ELIMINAR
// ============================================
async function cargarProducto(id) {
    try {
        const response = await fetch(`/api/products/${id}`, { credentials: 'same-origin' });
        const data = await response.json();
        return data.success ? data.producto : null;
    } catch (error) {
        console.error('Error al cargar producto:', error);
        return null;
    }
}

async function enviarProducto(url, metodo, datos) {
    try {
        const response = await fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(datos)
        });
        return await response.json();
    } catch (error) {
        console.error('Error al guardar producto:', error);
        return { success: false, error: 'Error de conexión' };
    }
}

const crearProducto = (datos) => enviarProducto('/api/products/', 'POST', datos);
const actualizarProducto = (id, datos) => enviarProducto(`/api/products/${id}`, 'PUT', datos);

async function eliminarProducto(id, nombre, volverALista = false) {
    if (!confirm(`¿Eliminar el producto "${nombre}"?`)) return;

    try {
        const response = await fetch(`/api/products/${id}`, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            if (volverALista) {
                window.location.href = '/products/';
            } else {
                cargarProductos();
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
async function guardarFormulario(event, productoId = null) {
    event.preventDefault();

    const precio = parseFloat(document.getElementById('precio').value);
    const stock = parseInt(document.getElementById('stock').value, 10);

    if (Number.isNaN(precio) || Number.isNaN(stock) || precio < 0 || stock < 0) {
        alert('Precio y stock deben ser números mayores o iguales a 0');
        return;
    }

    const datos = {
        nombre: document.getElementById('nombre').value.trim(),
        sku: document.getElementById('sku').value.trim().toUpperCase(),
        categoria: document.getElementById('categoria').value.trim(),
        descripcion: document.getElementById('descripcion').value.trim(),
        precio: precio,
        stock: stock,
        estado: document.getElementById('estado')?.value || 'Activo'
    };

    const resultado = productoId
        ? await actualizarProducto(productoId, datos)
        : await crearProducto(datos);

    if (resultado.success) {
        window.location.href = '/products/';
    } else {
        alert('Error: ' + resultado.error);
    }
}

async function cargarDatosFormulario(productoId) {
    const producto = await cargarProducto(productoId);
    if (!producto) return;

    document.getElementById('nombre').value = producto.nombre || '';
    document.getElementById('sku').value = producto.sku || '';
    document.getElementById('categoria').value = producto.categoria || '';
    document.getElementById('descripcion').value = producto.descripcion || '';
    document.getElementById('precio').value = producto.precio ?? 0;
    document.getElementById('stock').value = producto.stock ?? 0;
    const estadoSelect = document.getElementById('estado');
    if (estadoSelect) estadoSelect.value = producto.estado || 'Activo';
}

// ============================================
// DETALLE
// ============================================
async function mostrarDetalle(productoId) {
    const contenedor = document.getElementById('detalle-producto-card');
    const producto = await cargarProducto(productoId);

    if (!producto) {
        contenedor.innerHTML = `
            <div class="detalle-body text-center py-5">
                <i class="bi bi-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
                <h4 class="mt-3">Producto no encontrado</h4>
                <a href="/products/" class="btn-gold mt-3">Volver a la lista</a>
            </div>`;
        return;
    }

    const fecha = producto.created_at
        ? new Date(/(Z|[+-]\d\d:\d\d)$/.test(producto.created_at) ? producto.created_at : producto.created_at + 'Z').toLocaleDateString('es-ES', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        })
        : '—';

    contenedor.innerHTML = `
        <div class="detalle-header">
            <h4><i class="bi bi-box-seam"></i> ${escaparHtml(producto.nombre)}</h4>
            ${badgeEstado(producto.estado)}
        </div>
        <div class="detalle-body">
            <div class="detalle-fila"><span class="label">ID</span><span class="valor">#${producto.id}</span></div>
            <div class="detalle-fila"><span class="label">SKU</span><span class="valor"><strong>${escaparHtml(producto.sku)}</strong></span></div>
            <div class="detalle-fila"><span class="label">Categoría</span><span class="valor">${escaparHtml(producto.categoria) || '—'}</span></div>
            <div class="detalle-fila"><span class="label">Descripción</span><span class="valor">${escaparHtml(producto.descripcion) || '—'}</span></div>
            <div class="detalle-fila"><span class="label">Precio</span><span class="valor">${formatearPrecio(producto.precio)}</span></div>
            <div class="detalle-fila"><span class="label">Stock</span><span class="valor">${formatearStock(producto.stock)} unidades</span></div>
            <div class="detalle-fila"><span class="label">Fecha de registro</span><span class="valor">${fecha}</span></div>
        </div>
        <div class="detalle-footer">
            <button type="button" class="btn btn-outline-danger btn-eliminar-detalle"
                    data-id="${producto.id}" data-nombre="${escaparHtml(producto.nombre)}">
                <i class="bi bi-trash"></i> Eliminar
            </button>
            <a href="/products/${producto.id}/edit" class="btn-gold">
                <i class="bi bi-pencil"></i> Editar
            </a>
        </div>`;
}

// ============================================
// INICIALIZACIÓN AUTOMÁTICA
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Listado
    const lista = document.getElementById('lista-productos');
    if (lista) {
        cargarProductos();
        lista.addEventListener('click', (e) => {
            const boton = e.target.closest('.btn-eliminar');
            if (boton) eliminarProducto(boton.dataset.id, boton.dataset.nombre);
        });
    }

    // Formulario (crear o editar)
    const form = document.getElementById('form-producto');
    if (form) {
        const productoId = form.dataset.productoId || null;
        form.addEventListener('submit', (e) => guardarFormulario(e, productoId));
        if (productoId) cargarDatosFormulario(productoId);
    }

    // Detalle
    const detalle = document.getElementById('detalle-producto-card');
    if (detalle) {
        mostrarDetalle(detalle.dataset.productoId);
        detalle.addEventListener('click', (e) => {
            const boton = e.target.closest('.btn-eliminar-detalle');
            if (boton) eliminarProducto(boton.dataset.id, boton.dataset.nombre, true);
        });
    }
});