// ============================================
// HERMES Dashboard - lógica de datos en vivo
// ============================================

let chartVentas = null;
let chartEstado = null;
let diasSeleccionados = 30;

const COLOR_ESTADO = {
    completado: '#2ecc71',
    pendiente: '#4d94ff',
    atrasado: '#ffb020',
    cancelado: '#e74c3c',
};

const ETIQUETA_ESTADO = {
    completado: 'Completados',
    pendiente: 'Pendientes',
    atrasado: 'En progreso',
    cancelado: 'Cancelados',
};

document.addEventListener('DOMContentLoaded', () => {
    cargarTodo();
    document.getElementById('btnRefrescar').addEventListener('click', () => cargarTodo(true));
    document.getElementById('btnReintentar').addEventListener('click', () => cargarTodo(true));

    document.querySelectorAll('#selectorPeriodo button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#selectorPeriodo button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            diasSeleccionados = parseInt(btn.dataset.dias, 10);
            cargarVentas();
        });
    });

    setInterval(() => cargarTodo(false, true), 60000);
});

async function cargarTodo(manual = false, silencioso = false) {
    ocultarErrorGlobal();
    if (manual) girarIconoRefrescar(true);

    const resultados = await Promise.allSettled([
        cargarStats(silencioso),
        cargarVentas(silencioso),
        cargarAlertas(silencioso),
        cargarActividades(silencioso),
    ]);

    if (resultados.some(r => r.status === 'rejected') && !silencioso) mostrarErrorGlobal();
    marcarUltimaActualizacion();
    if (manual) setTimeout(() => girarIconoRefrescar(false), 400);
}

async function fetchJSON(url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

// ---------- Métricas ----------
async function cargarStats(silencioso = false) {
    try {
        const data = await fetchJSON('/api/dashboard/stats');
        const stats = data.stats || {};
        ['clientes', 'proveedores', 'productos', 'pedidos', 'envios', 'ingresos'].forEach(key => {
            const card = document.querySelector(`[data-metric="${key}"]`);
            if (!card) return;
            card.classList.remove('metric-skeleton');

            const valor = stats[key];
            const cambio = stats[`cambio_${key}`];
            const esMoneda = card.dataset.currency === 'true';

            animarNumero(card.querySelector('.metric-value'), valor || 0, esMoneda);

            const changeEl = card.querySelector('.metric-change');
            if (typeof cambio === 'number') {
                const positivo = cambio >= 0;
                changeEl.className = `metric-change ${positivo ? 'text-success' : 'text-danger'}`;
                changeEl.innerHTML = `<i class="bi bi-arrow-${positivo ? 'up' : 'down'}"></i> ${Math.abs(cambio).toFixed(1)}% vs mes pasado`;
            }
        });
    } catch (err) {
        if (!silencioso) console.error('Error cargando stats:', err);
        throw err;
    }
}

function animarNumero(el, valorFinal, esMoneda) {
    const duracion = 800;
    const inicio = performance.now();
    function frame(ahora) {
        const progreso = Math.min((ahora - inicio) / duracion, 1);
        const actual = valorFinal * progreso;
        el.textContent = esMoneda ? formatoMoneda(actual) : Math.round(actual).toLocaleString('es-SV');
        if (progreso < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
}

function formatoMoneda(valor) {
    return '$' + valor.toLocaleString('es-SV', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ---------- Ventas + estado ----------
async function cargarVentas(silencioso = false) {
    try {
        const data = await fetchJSON(`/api/dashboard/sales-chart?dias=${diasSeleccionados}`);
        const labels = data.labels || [];
        const valores = data.valores || [];
        const estados = data.pedidos_por_estado || {};

        const vacio = valores.length === 0 || valores.every(v => !v);
        document.getElementById('ventasEmpty').classList.toggle('d-none', !vacio);
        document.getElementById('ventasChart').classList.toggle('d-none', vacio);

        if (!vacio) {
            const total = valores.reduce((a, b) => a + b, 0);
            document.getElementById('ventasTotalTexto').textContent = formatoMoneda(total);
            const mitad = Math.floor(valores.length / 2);
            const primeraMitad = valores.slice(0, mitad).reduce((a, b) => a + b, 0) || 1;
            const segundaMitad = valores.slice(mitad).reduce((a, b) => a + b, 0);
            const variacion = ((segundaMitad - primeraMitad) / primeraMitad) * 100;
            const elVar = document.getElementById('ventasVsPeriodo');
            elVar.className = variacion >= 0 ? 'text-success' : 'text-danger';
            elVar.innerHTML = `<i class="bi bi-arrow-${variacion >= 0 ? 'up' : 'down'}"></i> ${Math.abs(variacion).toFixed(1)}% vs período anterior`;

            renderVentasChart(labels, valores);
        }
        renderEstadoChart(estados);
    } catch (err) {
        if (!silencioso) console.error('Error cargando gráfica de ventas:', err);
        throw err;
    }
}

function renderVentasChart(labels, valores) {
    const ctx = document.getElementById('ventasChart');
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
                pointRadius: 0,
                pointHoverRadius: 5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (ctx) => ' ' + formatoMoneda(ctx.parsed.y) } }
            },
            scales: {
                x: { grid: { color: '#262c36' }, ticks: { color: '#8b929e' } },
                y: { beginAtZero: true, grid: { color: '#262c36' }, ticks: { color: '#8b929e', callback: (v) => v >= 1000 ? (v / 1000) + 'k' : v } }
            }
        }
    });
}

function renderEstadoChart(estados) {
    const ctx = document.getElementById('estadoChart');
    const claves = Object.keys(estados);
    const valores = Object.values(estados);
    const total = valores.reduce((a, b) => a + b, 0);

    document.getElementById('donutTotal').textContent = total.toLocaleString('es-SV');

    if (chartEstado) chartEstado.destroy();
    chartEstado = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: claves.map(k => ETIQUETA_ESTADO[k] || k),
            datasets: [{
                data: valores,
                backgroundColor: claves.map(k => COLOR_ESTADO[k] || '#d4af37'),
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '72%',
            plugins: { legend: { display: false }, tooltip: { enabled: true } }
        }
    });

    const leyenda = document.getElementById('leyendaEstado');
    leyenda.innerHTML = claves.map(k => {
        const pct = total ? Math.round((estados[k] / total) * 100) : 0;
        return `
            <div class="item">
                <span class="dot" style="background:${COLOR_ESTADO[k] || '#d4af37'}"></span>
                <div>
                    <div class="label">${ETIQUETA_ESTADO[k] || k}</div>
                    <div class="valor">${estados[k].toLocaleString('es-SV')} (${pct}%)</div>
                </div>
            </div>
        `;
    }).join('');
}

// ---------- Actividades recientes ----------
async function cargarActividades(silencioso = false) {
    const cont = document.getElementById('listaActividades');
    try {
        const data = await fetchJSON('/api/dashboard/activities');
        const items = data.activities || [];
        if (items.length === 0) {
            cont.innerHTML = '<div class="text-muted small">Sin actividad reciente</div>';
            return;
        }
        const iconos = { pedido: 'bi-cart-check-fill text-success', correo: 'bi-envelope-fill text-info', envio: 'bi-truck text-warning' };
        cont.innerHTML = items.map(a => `
            <div class="hermes-list-item">
                <span><i class="bi ${iconos[a.tipo] || 'bi-clock-history'} me-2"></i>${a.texto}</span>
                <span class="time">${a.tiempo}</span>
            </div>
        `).join('');
    } catch (err) {
        if (!silencioso) console.error('Error cargando actividades:', err);
        cont.innerHTML = '<div class="text-danger small"><i class="bi bi-exclamation-circle me-2"></i>No se pudieron cargar las actividades</div>';
        throw err;
    }
}

// ---------- Alertas / Recordatorios ----------
async function cargarAlertas(silencioso = false) {
    const cont = document.getElementById('listaAlertas');
    try {
        const data = await fetchJSON('/api/dashboard/alerts');
        const alertas = data.alerts || [];
        if (alertas.length === 0) {
            cont.innerHTML = '<div class="text-muted small">Sin pendientes 🎉</div>';
            return;
        }
        const iconos = { danger: 'bi-exclamation-circle-fill text-danger', warning: 'bi-exclamation-triangle-fill text-warning', info: 'bi-envelope-fill text-info' };
        cont.innerHTML = alertas.map(a => `
            <div class="hermes-list-item">
                <span><i class="bi ${iconos[a.tipo] || iconos.info} me-2"></i>${a.mensaje}</span>
                <a href="${a.url || '#'}" class="text-gold">Ver</a>
            </div>
        `).join('');
    } catch (err) {
        if (!silencioso) console.error('Error cargando alertas:', err);
        cont.innerHTML = '<div class="text-danger small"><i class="bi bi-exclamation-circle me-2"></i>No se pudieron cargar los recordatorios</div>';
        throw err;
    }
}

// ---------- UI helpers ----------
function mostrarErrorGlobal() { document.getElementById('alertaErrorGlobal').classList.remove('d-none'); }
function ocultarErrorGlobal() { document.getElementById('alertaErrorGlobal').classList.add('d-none'); }
function girarIconoRefrescar(activo) { document.getElementById('iconoRefrescar').classList.toggle('spin', activo); }
function marcarUltimaActualizacion() {
    const el = document.getElementById('ultima-actualizacion');
    el.textContent = 'Actualizado a las ' + new Date().toLocaleTimeString('es-SV', { hour: '2-digit', minute: '2-digit' });
}