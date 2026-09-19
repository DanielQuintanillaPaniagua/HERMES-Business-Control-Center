async function cargarClientes() {
    const contenedor = document.getElementById('lista-clientes');
    if (!contenedor) return;

    try {
        const response = await fetch('/api/clients/', {
            credentials: 'same-origin'
        });

        if (response.status === 401) {
            window.location.href = '/auth/login';
            return;
        }

        const data = await response.json();

        if (!data.success) {
            contenedor.innerHTML = '<p class="text-danger">Error al cargar clientes</p>';
            return;
        }

        if (data.clientes.length === 0) {
            contenedor.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-people" style="font-size: 3rem; color: #d4af37;"></i>
                    <h4 class="mt-3">No hay clientes registrados</h4>
                    <p class="text-muted">Empieza creando tu primer cliente</p>
                    <a href="/clients/new" class="btn btn-gold">
                        <i class="bi bi-plus-circle"></i> Crear primer cliente
                    </a>
                </div>
            `;
            return;
        }

        let html = `
            <table class="table table-hover">
                <thead style="background-color: #1a1a1a; color: #d4af37;">
                    <tr>
                        <th>#</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Teléfono</th>
                        <th>Ciudad</th>
                        <th>Estado</th>
                        <th class="text-end">Acciones</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.clientes.forEach(c => {
            const badge = c.estado === 'Activo'
                ? '<span class="badge bg-success">Activo</span>'
                : '<span class="badge bg-secondary">Inactivo</span>';

            html += `
                <tr>
                    <td>${c.id}</td>
                    <td><strong>${c.nombre}</strong></td>
                    <td>${c.email}</td>
                    <td>${c.telefono || '—'}</td>
                    <td>${c.ciudad || '—'}</td>
                    <td>${badge}</td>
                    <td class="text-end">
                        <a href="/clients/${c.id}" class="btn btn-sm btn-outline-primary" title="Ver">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="/clients/${c.id}/edit" class="btn btn-sm btn-outline-warning" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button onclick="eliminarCliente(${c.id}, '${c.nombre}')" 
                                class="btn btn-sm btn-outline-danger" title="Eliminar">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        contenedor.innerHTML = html;

    } catch (error) {
        console.error('Error al cargar clientes:', error);
        contenedor.innerHTML = '<p class="text-danger">Error de conexión</p>';
    }
}

// CARGAR UN CLIENTE (para el formulario de editar o detalle)
async function cargarCliente(id) {
    try {
        const response = await fetch(`/api/clients/${id}`, {
            credentials: 'same-origin'
        });
        const data = await response.json();
        return data.cliente;
    } catch (error) {
        console.error('Error al cargar cliente:', error);
        return null;
    }
}

// CREAR CLIENTE
async function crearCliente(datos) {
    try {
        const response = await fetch('/api/clients/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(datos)
        });
        return await response.json();
    } catch (error) {
        console.error('Error al crear cliente:', error);
        return { success: false, error: 'Error de conexión' };
    }
}

// ACTUALIZAR CLIENTE
async function actualizarCliente(id, datos) {
    try {
        const response = await fetch(`/api/clients/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(datos)
        });
        return await response.json();
    } catch (error) {
        console.error('Error al actualizar cliente:', error);
        return { success: false, error: 'Error de conexión' };
    }
}

// ELIMINAR CLIENTE

async function eliminarCliente(id, nombre) {
    if (!confirm(`¿Eliminar al cliente "${nombre}"?`)) return;

    try {
        const response = await fetch(`/api/clients/${id}`, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            cargarClientes();  // Recargar la lista
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error de conexión');
    }
}

// MANEJAR FORMULARIO (crear/editar)

async function guardarFormulario(event, clienteId = null) {
    event.preventDefault();

    const datos = {
        nombre: document.getElementById('nombre').value.trim(),
        email: document.getElementById('email').value.trim(),
        telefono: document.getElementById('telefono').value.trim(),
        ciudad: document.getElementById('ciudad').value.trim(),
        estado: document.getElementById('estado')?.value || 'Activo'
    };

    let resultado;
    if (clienteId) {
        resultado = await actualizarCliente(clienteId, datos);
    } else {
        resultado = await crearCliente(datos);
    }

    if (resultado.success) {
        window.location.href = '/clients/';
    } else {
        alert('Error: ' + resultado.error);
    }
}


// CARGAR DATOS EN FORMULARIO DE EDICIÓN
async function cargarDatosFormulario(clienteId) {
    const cliente = await cargarCliente(clienteId);
    if (!cliente) return;

    document.getElementById('nombre').value = cliente.nombre || '';
    document.getElementById('email').value = cliente.email || '';
    document.getElementById('telefono').value = cliente.telefono || '';
    document.getElementById('ciudad').value = cliente.ciudad || '';
    const estadoSelect = document.getElementById('estado');
    if (estadoSelect) estadoSelect.value = cliente.estado || 'Activo';

    // Configurar el submit
    const form = document.getElementById('form-cliente');
    if (form) {
        form.addEventListener('submit', (e) => guardarFormulario(e, clienteId));
    }
}

// ============================================
// INICIALIZACIÓN AUTOMÁTICA
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Si estamos en la página de listado
    if (document.getElementById('lista-clientes')) {
        cargarClientes();
    }

    // Si estamos en la página de edición (con atributo data-cliente-id)
    const formEditar = document.getElementById('form-cliente');
    if (formEditar && formEditar.dataset.clienteId) {
        cargarDatosFormulario(formEditar.dataset.clienteId);
    }

    // Si estamos en la página de creación (form sin data-cliente-id)
    if (formEditar && !formEditar.dataset.clienteId) {
        formEditar.addEventListener('submit', (e) => guardarFormulario(e, null));
    }
});