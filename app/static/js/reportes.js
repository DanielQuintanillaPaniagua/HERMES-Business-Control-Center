/* ==========================================================================
   HERMES - Pantalla de Reportes / Analíticas
   - Dibuja las 4 tarjetas de resumen
   - Dibuja el gráfico de línea "Ventas por día" y el donut "Ventas por categoría"
   - loadReportData() es donde se conecta con el backend real (Flask).
     Por ahora usa MOCK_DATA para poder maquetar sin depender del equipo de backend.
   ========================================================================== */

const MOCK_DATA = {
    summary: [
        { label: "Ventas totales", value: "$24,780.00", delta: "+15.8% vs mes pasado", down: false },
        { label: "Pedidos totales", value: "3,240", delta: "+8.7% vs mes pasado", down: false },
        { label: "Clientes nuevos", value: "156", delta: "+12.1% vs mes pasado", down: false },
        { label: "Ticket promedio", value: "$187.45", delta: "+7.3% vs mes pasado", down: false }
    ],
    ventasPorDia: {
        labels: ["1 May", "8 May", "15 May", "22 May", "29 May", "5 Jun"],
        values: [8200, 12400, 9800, 15600, 13100, 18900]
    },
    ventasPorCategoria: [
        { label: "Electrónicos", value: 45, color: "#4fa3f7" },
        { label: "Alimentos", value: 25, color: "#3ecf8e" },
        { label: "Hogar", value: 15, color: "#f2a93b" },
        { label: "Otros", value: 15, color: "#8b909c" }
    ]
};

async function loadReportData(tab = "ventas") {
    return new Promise((resolve) => setTimeout(() => resolve(MOCK_DATA), 150));
}

function renderSummary(summary) {
    const grid = document.getElementById("summaryGrid");
    grid.innerHTML = summary
        .map(
            (item) => `
      <div class="card summary-card">
        <p class="card-title" style="color:var(--text-dim); font-weight:500;">${item.label}</p>
        <div class="value">${item.value}</div>
        <div class="delta ${item.down ? "down" : ""}">${item.down ? "▼" : "▲"} ${item.delta}</div>
      </div>`
        )
        .join("");
}

let lineChart, donutChart;

function renderLineChart(ventasPorDia) {
    const ctx = document.getElementById("salesLineChart");
    if (lineChart) lineChart.destroy();
    lineChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: ventasPorDia.labels,
            datasets: [
                {
                    label: "Ventas",
                    data: ventasPorDia.values,
                    borderColor: "#f2a93b",
                    backgroundColor: "rgba(242,169,59,0.12)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 3,
                    pointBackgroundColor: "#f2a93b"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: "#1c202b" }, ticks: { color: "#8b909c" } },
                y: { grid: { color: "#1c202b" }, ticks: { color: "#8b909c" } }
            }
        }
    });
}

function renderDonutChart(ventasPorCategoria) {
    const ctx = document.getElementById("categoryDonutChart");
    if (donutChart) donutChart.destroy();
    donutChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ventasPorCategoria.map((c) => c.label),
            datasets: [
                {
                    data: ventasPorCategoria.map((c) => c.value),
                    backgroundColor: ventasPorCategoria.map((c) => c.color),
                    borderWidth: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: { legend: { display: false } }
        }
    });

    const legend = document.getElementById("donutLegend");
    legend.innerHTML = ventasPorCategoria
        .map(
            (c) => `
      <div class="donut-legend-item">
        <span class="dot" style="background:${c.color}"></span>
        ${c.label}
        <span class="pct">${c.value}%</span>
      </div>`
        )
        .join("");
}

async function initReportTab(tab) {
    const data = await loadReportData(tab);
    renderSummary(data.summary);
    renderLineChart(data.ventasPorDia);
    renderDonutChart(data.ventasPorCategoria);
}

document.querySelectorAll(".tab").forEach((tabEl) => {
    tabEl.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
        tabEl.classList.add("active");
        initReportTab(tabEl.dataset.tab);
    });
});

initReportTab("ventas");