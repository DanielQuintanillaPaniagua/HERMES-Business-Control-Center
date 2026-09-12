document.addEventListener('DOMContentLoaded', function () {

    // 1. Auto-cerrar mensajes flash después de 4 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });

    // 2. Confirmación antes de cerrar sesión
    const logoutBtn = document.querySelector('a[href*="logout"]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            if (!confirm('¿Seguro que quieres cerrar sesión?')) {
                e.preventDefault();
            }
        });
    }

    // 3. Log para confirmar que el JS carga
    console.log('✅ HERMES: main.js cargado');
});