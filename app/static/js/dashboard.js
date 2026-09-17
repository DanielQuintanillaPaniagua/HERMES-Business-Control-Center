// dashboard.js — Consume las APIs del dashboard (Prioridad 1)
// Endpoints usados:
//   GET /api/dashboard/stats
//   GET /api/dashboard/sales-chart?dias=30
//   GET /api/dashboard/alerts

const METRICAS = [
    { key: 'clientes', label: 'Clientes', icon: 'bi-people-fill', color: 'primary' },
    { key: 'proveedores', label: 'Proveedores', icon: 'bi-truck', color: 'info' },
    { key: 'productos', label: 'Productos', icon: 'bi-box-seam-fill', color: 'secondary' },
    { key: 'pedidos', label: 'Pedidos', icon: 'bi-cart-check-fill', color: 'success' },
    { key: 'envios', label: 'Envíos', icon: 'bi-send-fill', color: 'info' },
    { key: 'ingresos', label: 'Ingresos', icon: 'bi-cash-coin', color: 'gold', money: true },
];

document.addEventListener('DOMContentLoaded', () => {
    renderSkeletons();
    cargarStats();
    cargarChartVentas();
    cargarAlertas();
});

// --- 1. Tarjetas de métricas -------------------------------------------------

function renderSkeletons() {
    const cont = document.getElementById('dashboard-stats');
    cont.innerHTML = METRICAS.map(m => `
    <div class="col-6 col-md-4 col-xl-2">
      <div class="metric-card" data-key="${m.key}">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <h6 class="text-muted mb-1">${m.label}</h6>
            <div class="skeleton-line"></div>
          </div>
          <span class="metric-icon ${m.color === 'gold' ? 'bg-gold text-gold' : `bg-${m.color} bg-opacity-10 text-${m.color}`}">
            <i class="bi ${m.icon}"></i>
          </span>
        </div>
      </div>
    </div>
  `).join('');
}

async function cargarStats() {
    try {
        const res = await fetch('/api/dashboard/stats', { credentials: 'same-origin' });
        const data = await res.json();
        if (!data.success) throw new Error('Respuesta sin success');

        // Acepta tanto {stats: {...}} como los campos sueltos en la raíz
        const stats = data.stats || data;

        METRICAS.forEach(m => {
            const card = document.querySelector(`.metric-card[data-key="${m.key}"]`);
            if (!card) return;

            const valor = stats[m.key] ?? stats[`total_${m.key}`] ?? 0;
            const cambio = stats[`cambio_${m.key}`];

            card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <h6 class="text-muted mb-1">${m.label}</h6>
            <h3 class="metric-value" data-target="${valor}">0</h3>
          </div>
          <span class="metric-icon ${m.color === 'gold' ? 'bg-gold text-gold' : `bg-${m.color} bg-opacity-10 text-${m.color}`}">
            <i class="bi ${m.icon}"></i>
          </span>
        </div>
        ${cambio !== undefined ? `
          <small class="${cambio >= 0 ? 'text-success' : 'text-danger'}">
            <i class="bi bi-arrow-${cambio >= 0 ? 'up' : 'down'}"></i>
            ${Math.abs(cambio).toFixed(1)}% vs mes pasado
          </small>` : ''}
      `;

            animarContador(card.querySelector('.metric-value'), Number(valor) || 0, m.money);
        });
    } catch (err) {
        console.error('Error cargando stats:', err);
        document.getElementById('dashboard-stats').innerHTML =
            `<div class="col-12"><div class="alert alert-warning">No se pudieron cargar las métricas.</div></div>`;
    }
}

function animarContador(el, valorFinal, esMoneda = false) {
    const duracion = 900;
    const inicio = performance.now();

    function paso(ahora) {
        const progreso = Math.min((ahora - inicio) / duracion, 1);
        const actual = valorFinal * progreso;
        el.textContent = esMoneda
            ? '$' + actual.toLocaleString('es-SV', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : Math.floor(actual).toLocaleString('es-SV');
        if (progreso < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
}

// --- 2. Gráfica de ventas (línea) -------------------------------------------

async function cargarChartVentas() {
    try {
        const res = await fetch('/api/dashboard/sales-chart?dias=30', { credentials: 'same-origin' });
        const data = await res.json();
        if (!data.success) throw new Error('Respuesta sin success');

        // Ajusta estos nombres si el backend usa otros distintos
        const labels = data.labels || data.dias || data.fechas || [];
        const valores = data.valores || data.ventas || data.datos || [];

        const canvas = document.getElementById('chart-ventas');
        new Chart(canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Ventas',
                    data: valores,
                    borderColor: '#d4af37',
                    backgroundColor: crearGradienteOro(canvas),
                    tension: 0.35,
                    fill: true,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                }]
            },
            options: {
                responsive: true,
                animation: { duration: 900, easing: 'easeOutQuart' },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => '$' + Number(ctx.parsed.y).toLocaleString('es-SV')
                        }
                    }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { callback: (v) => '$' + v.toLocaleString('es-SV') } }
                }
            }
        });

        cargarChartPedidos(data.pedidos_por_estado);
    } catch (err) {
        console.error('Error cargando gráfica de ventas:', err);
    }
}

function crearGradienteOro(canvas) {
    const ctx = canvas.getContext('2d');
    const gradiente = ctx.createLinearGradient(0, 0, 0, 300);
    gradiente.addColorStop(0, 'rgba(212,175,55,0.35)');
    gradiente.addColorStop(1, 'rgba(212,175,55,0)');
    return gradiente;
}

// --- 3. Gráfica de pedidos por estado (dona) --------------------------------

async function cargarChartPedidos(pedidosPreCargados) {
    try {
        let pedidosPorEstado = pedidosPreCargados;

        // Si /sales-chart no trae el desglose, lo calculamos con /api/orders/
        if (!pedidosPorEstado) {
            const res = await fetch('/api/orders/', { credentials: 'same-origin' });
            const data = await res.json();
            pedidosPorEstado = {};
            (data.pedidos || data.orders || []).forEach(p => {
                pedidosPorEstado[p.estado] = (pedidosPorEstado[p.estado] || 0) + 1;
            });
        }

        const coloresEstado = {
            completado: '#28a745',
            pendiente: '#fd7e14',
            atrasado: '#dc3545',
            cancelado: '#6c757d',
        };

        const labels = Object.keys(pedidosPorEstado);
        const valores = Object.values(pedidosPorEstado);

        new Chart(document.getElementById('chart-pedidos'), {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: valores,
                    backgroundColor: labels.map(l => coloresEstado[l] || '#adb5bd'),
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                animation: { animateRotate: true, duration: 900 },
                plugins: { legend: { position: 'bottom' } }
            }
        });
    } catch (err) {
        console.error('Error cargando gráfica de pedidos:', err);
    }
}

// --- 4. Panel de alertas -----------------------------------------------------

async function cargarAlertas() {
    const cont = document.getElementById('dashboard-alerts');
    try {
        const res = await fetch('/api/dashboard/alerts', { credentials: 'same-origin' });
        const data = await res.json();
        if (!data.success) throw new Error('Respuesta sin success');

        const alertas = data.alerts || data.alertas || [];

        if (alertas.length === 0) {
            cont.innerHTML = `
        <div class="metric-card text-center py-4">
          <i class="bi bi-check-circle-fill text-success fs-2"></i>
          <p class="text-muted mb-0 mt-2">Sin pendientes, todo al día 🎉</p>
        </div>`;
            return;
        }

        const iconosPorTipo = {
            danger: 'bi-exclamation-octagon-fill text-danger',
            warning: 'bi-exclamation-triangle-fill text-warning',
            info: 'bi-info-circle-fill text-info',
        };

        cont.innerHTML = `
      <div class="metric-card">
        <h6 class="text-muted mb-3">Alertas</h6>
        <ul class="list-unstyled mb-0">
          ${alertas.map((a, i) => `
            <li class="d-flex justify-content-between align-items-center py-2 ${i < alertas.length - 1 ? 'border-bottom' : ''} alerta-item" style="animation-delay:${i * 60}ms">
              <span>
                <i class="bi ${iconosPorTipo[a.tipo] || iconosPorTipo.info} me-2"></i>
                ${a.mensaje || a.texto}
              </span>
              ${a.url ? `<a href="${a.url}" class="text-gold text-decoration-none">Ver</a>` : ''}
            </li>
          `).join('')}
        </ul>
      </div>`;
    } catch (err) {
        console.error('Error cargando alertas:', err);
        cont.innerHTML = `<div class="alert alert-warning">No se pudieron cargar las alertas.</div>`;
    }
}