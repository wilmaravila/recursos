// static/js/graficas.js
function cargarGraficas(DATOS) {
    // Validaciones básicas
    const fechas = DATOS.fechas || [];
    const montosGastos = DATOS.montosGastos || [];
    const fechasIng = DATOS.fechasIng || [];
    const montosIngresos = DATOS.montosIngresos || [];
    const labelsGastos = DATOS.labelsGastos || [];
    const valoresGastos = DATOS.valoresGastos || [];

    // UTILS: si no hay datos, coloca un placeholder para que Chart.js no rompa
    function isEmptyArray(a){ return !Array.isArray(a) || a.length === 0; }

    // === GRÁFICA DE BARRAS/LINE (Ingresos vs Gastos) ===
    const elBarras = document.getElementById("chartBarras");
    if (elBarras) {
        if (isEmptyArray(fechas) && isEmptyArray(fechasIng)) {
            // muestra mensaje dentro del canvas (si lo deseas)
            const ctx = elBarras.getContext('2d');
            ctx.font = "16px Arial";
            ctx.fillText("No hay datos para mostrar.", 20, 50);
        } else {
            // elegimos etiquetas: si hay más fechas de ingresos, las usamos; sino las de gastos
            const labels = (fechasIng.length >= fechas.length) ? fechasIng : fechas;
            const dataIngresos = montosIngresos.length ? montosIngresos : labels.map(()=>0);
            const dataGastos = montosGastos.length ? montosGastos : labels.map(()=>0);

            new Chart(elBarras, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Ingresos",
                            data: dataIngresos,
                            backgroundColor: 'rgba(75, 192, 192, 0.6)'
                        },
                        {
                            label: "Gastos",
                            data: dataGastos,
                            backgroundColor: 'rgba(255, 99, 132, 0.6)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    interaction: { mode: 'index', intersect: false },
                    scales: { y: { beginAtZero: true } }
                }
            });
        }
    }

    // === DONUT / PIE para distribución de gastos ===
    const elDonut = document.getElementById("chartGastos");
    if (elDonut) {
        if (isEmptyArray(labelsGastos) || isEmptyArray(valoresGastos)) {
            const ctx = elDonut.getContext('2d');
            ctx.font = "14px Arial";
            ctx.fillText("No hay datos para el donut", 20, 50);
        } else {
            new Chart(elDonut, {
                type: "doughnut",
                data: {
                    labels: labelsGastos,
                    datasets: [{
                        data: valoresGastos,
                        backgroundColor: [
                            "#4e73df","#1cc88a","#36b9cc","#f6c23e","#e74a3b","#6f42c1"
                        ]
                    }]
                },
                options: { responsive: true }
            });
        }
    }
}
