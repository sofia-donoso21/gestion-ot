function validateForm() {
    const user = document.querySelector('input[name="user"]').value;
    const password = document.querySelector('input[name="password"]').value;

    if (!user || !password) {
        return false;
    }

    Swal.fire({
        title: 'Validando...',
        text: 'Por favor, espere mientras validamos sus credenciales.',
        allowOutsideClick: false,
        showConfirmButton: false,
        willOpen: () => {
            Swal.showLoading();
        }
    });

    fetch('/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'user': user,
            'password': password
        })
        // body: JSON.stringify({ user: user, password: password })
    })
        .then(response => response.json())
        .then(data => {
            Swal.close();

            if (data.code === 200) {
                // Swal.fire({
                //     icon: 'success',
                //     title: 'Acceso concedido',
                //     text: 'Bienvenido, ha ingresado correctamente.',
                //     allowOutsideClick: false,
                //     showConfirmButton: false,
                // }).then(() => {
                //     // Redirigir a otra página o realizar una acción
                //     window.location.href = '/inicio'; // Cambia esto según tu necesidad
                // });
                Swal.fire({
                    icon: 'success',
                    title: 'Acceso concedido',
                    text: 'Bienvenido, ha ingresado correctamente.',
                    allowOutsideClick: false,
                    showConfirmButton: false,
                    timer: 3000, // 3000 milisegundos = 3 segundos
                    timerProgressBar: true, // Muestra una barra de progreso
                }).then(() => {
                    // Redirigir a otra página después de que la alerta se cierre
                    window.location.href = '/inicio'; // Cambia esto según tu necesidad
                });

            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Acceso denegado',
                    text: 'Credenciales incorrectas, por favor intente nuevamente.'
                });
            }
        })
        .catch(error => {
            Swal.close();
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un error al procesar su solicitud.'
            });
            console.error('Error:', error);
        });

    return false;
}

const SELECTOR_SIDEBAR_WRAPPER = ".sidebar-wrapper";
const Default = {
    scrollbarTheme: "os-theme-light",
    scrollbarAutoHide: "leave",
    scrollbarClickScroll: true,
};
document.addEventListener("DOMContentLoaded", function () {
    const sidebarWrapper = document.querySelector(SELECTOR_SIDEBAR_WRAPPER);
    if (
        sidebarWrapper &&
        typeof OverlayScrollbarsGlobal?.OverlayScrollbars !== "undefined"
    ) {
        OverlayScrollbarsGlobal.OverlayScrollbars(sidebarWrapper, {
            scrollbars: {
                theme: Default.scrollbarTheme,
                autoHide: Default.scrollbarAutoHide,
                clickScroll: Default.scrollbarClickScroll,
            },
        });
    }
});