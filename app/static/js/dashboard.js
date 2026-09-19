let chartVentas = null;
let chartPedidos = null;

const COLOR_ESTADO = {
    completado: '#2ecc71',
    pendiente: '#4d94ff',
    atrasado: '#ffb020',
    cancelado: '#e74c3c',
};

const ETIQUETA_ESTADO = {
    completado: 'Completados',
    pendiente: 'Pendientes',
    atrasado: 'Atrasados',
    cancelado: 'Cancelados',
};

document.addEventListener('DOMContentLoaded', () => {
    cargarTodo();
    setInterval(cargarTodo, 60000);
});

async function cargarTodo() {
    await Promise.allSettled([
        cargarStats(),
        cargarVentas(),
        cargarActividades(),
        cargarAlertas(),
    ]);
}

async function fetchJSON(url) {
    const resp = await fetch(url, { credentials: 'same-origin' });
    if (resp.status === 401) {
        window.location.href = '/auth/login';
        throw new Error('No autenticado');
    }
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

async function cargarStats() {
    try {
        const data = await fetchJSON('/api/dashboard/stats');
        const cont = document.getElementById('dashboard-stats');

        const metricas = [
            { key: 'clientes', icono: 'bi-people-fill', color: '#0d6efd', label: 'Clientes', valor: data.total_clientes, cambio: data.cambio_clientes },
            { key: 'pedidos', icono: 'bi-cart-fill', color: '#198754', label: 'Pedidos', valor: data.total_pedidos, cambio: data.cambio_pedidos },
            { key: 'envios', icono: 'bi-send-fill', color: '#8b5cf6', label: 'Envíos', valor: data.total_envios, cambio: data.cambio_envios },
            { key: 'ingresos', icono: 'bi-cash-coin', color: '#d4af37', label: 'Ingresos (Mes)', valor: data.ingresos_mes, moneda: true, cambio: data.cambio_ingresos },
        ];

        cont.innerHTML = metricas.map(m => {
            const cambio = m.cambio || 0;
            const positivo = cambio >= 0;
            const color = positivo ? '#2ecc71' : '#e74c3c';
            const flecha = positivo ? 'up' : 'down';
            const valorFormateado = m.moneda
                ? formatoMoneda(m.valor)
                : m.valor.toLocaleString('es-SV');

            return `
                <div class="col-md-6 col-lg-3">
                    <div class="metric-card" data-key="${m.key}">
                        <div class="d-flex align-items-center gap-3 mb-2">
                            <div class="metric-icon" style="background: ${m.color}20; color: ${m.color};">
                                <i class="bi ${m.icono}"></i>
                            </div>
                            <div class="text-muted small">${m.label}</div>
                        </div>
                        <div class="metric-value">${valorFormateado}</div>
                        <div class="small mt-1" style="color: ${color};">
                            <i class="bi bi-arrow-${flecha}"></i> ${Math.abs(cambio).toFixed(1)}% vs mes pasado
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error('Error cargando stats:', err);
    }
}

async function cargarVentas() {
    try {
        const data = await fetchJSON('/api/dashboard/sales-chart?dias=30');
        const labels = data.labels || [];
        const valores = data.data || [];
        const total = data.total || 0;

        document.getElementById('ventas-total').textContent = formatoMoneda(total);

        // Variación: comparar mitad vs mitad
        const mitad = Math.floor(valores.length / 2);
        const primera = valores.slice(0, mitad).reduce((a, b) => a + b, 0) || 1;
        const segunda = valores.slice(mitad).reduce((a, b) => a + b, 0);
        const variacion = ((segunda - primera) / primera) * 100;
        const positivo = variacion >= 0;
        document.getElementById('ventas-cambio').innerHTML = `
            <span style="color: ${positivo ? '#2ecc71' : '#e74c3c'};">
                <i class="bi bi-arrow-${positivo ? 'up' : 'down'}"></i>
                ${Math.abs(variacion).toFixed(1)}% vs período anterior
            </span>
        `;

        const ctx = document.getElementById('chart-ventas');
        if (chartVentas) chartVentas.destroy();
        chartVentas = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    data: valores,
                    borderColor: '#d4af37',
                    backgroundColor: 'rgba(212,175,55,0.15)',
                    tension: 0.35,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: '#d4af37',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: (c) => ' ' + formatoMoneda(c.parsed.y) } }
                },
                scales: {
                    x: { grid: { color: '#262c36' }, ticks: { color: '#8b929e', autoSkip: true, maxTicksLimit: 8 } },
                    y: { beginAtZero: true, grid: { color: '#262c36' }, ticks: { color: '#8b929e', callback: (v) => v >= 1000 ? (v / 1000) + 'k' : v } }
                }
            }
        });

        // Donut
        const stats = await fetchJSON('/api/dashboard/stats');
        const estados = stats.pedidos_por_estado || {};
        const claves = Object.keys(estados);
        const valoresEstados = Object.values(estados);
        const totalPedidos = valoresEstados.reduce((a, b) => a + b, 0);

        document.getElementById('donut-total-valor').textContent = totalPedidos.toLocaleString('es-SV');

        const ctx2 = document.getElementById('chart-pedidos');
        if (chartPedidos) chartPedidos.destroy();
        chartPedidos = new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: claves.map(k => ETIQUETA_ESTADO[k] || k),
                datasets: [{
                    data: valoresEstados,
                    backgroundColor: claves.map(k => COLOR_ESTADO[k] || '#d4af37'),
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: { legend: { display: false } }
            }
        });

        document.getElementById('leyenda-pedidos').innerHTML = claves.map(k => {
            const pct = totalPedidos ? Math.round((estados[k] / totalPedidos) * 100) : 0;
            return `
                <div class="d-flex justify-content-between align-items-center mb-2" style="font-size: 0.85rem;">
                    <div class="d-flex align-items-center gap-2">
                        <span style="width: 10px; height: 10px; border-radius: 50%; background: ${COLOR_ESTADO[k] || '#d4af37'};"></span>
                        <span style="color: #ccc;">${ETIQUETA_ESTADO[k] || k}</span>
                    </div>
                    <span style="color: #888;">${estados[k].toLocaleString('es-SV')} (${pct}%)</span>
                </div>
            `;
        }).join('');
    } catch (err) {
        console.error('Error cargando ventas:', err);
    }
}

async function cargarActividades() {
    const cont = document.getElementById('actividades-recientes');
    try {
        const data = await fetchJSON('/api/dashboard/activities');
        const items = data.activities || [];
        if (items.length === 0) {
            cont.innerHTML = '<p class="text-muted small">Sin actividad reciente</p>';
            return;
        }
        const iconos = { pedido: 'bi-cart-check text-success', envio: 'bi-truck text-warning', correo: 'bi-envelope text-info' };
        cont.innerHTML = items.map(a => `
            <div class="d-flex justify-content-between align-items-center py-2" style="border-bottom: 1px solid #2a2a2a;">
                <div style="color: #ccc; font-size: 0.9rem;">
                    <i class="bi ${iconos[a.tipo] || 'bi-clock'} me-2"></i>${a.texto}
                </div>
                <small style="color: #666;">${a.tiempo}</small>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error actividades:', err);
        cont.innerHTML = '<p class="text-danger small">Error</p>';
    }
}

async function cargarAlertas() {
    const cont = document.getElementById('recordatorios');
    try {
        const data = await fetchJSON('/api/dashboard/alerts');
        const alertas = data.alertas || [];
        if (alertas.length === 0) {
            cont.innerHTML = '<p class="text-muted small">Todo en orden 🎉</p>';
            return;
        }
        const iconos = { danger: 'bi-exclamation-circle-fill text-danger', warning: 'bi-exclamation-triangle-fill text-warning', info: 'bi-info-circle-fill text-info' };
        cont.innerHTML = alertas.map(a => `
            <div class="d-flex justify-content-between align-items-center py-2" style="border-bottom: 1px solid #2a2a2a;">
                <div style="color: #ccc; font-size: 0.9rem;">
                    <i class="bi ${iconos[a.tipo] || 'bi-info-circle'} me-2"></i>${a.titulo}
                </div>
                <a href="#" style="color: #d4af37; text-decoration: none; font-size: 0.85rem;">Ver</a>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error alertas:', err);
        cont.innerHTML = '<p class="text-danger small">Error</p>';
    }
}

function formatoMoneda(valor) {
    return '$' + (valor || 0).toLocaleString('es-SV', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}