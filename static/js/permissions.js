async function mostrarAlertaPermission () {
    const opcionesPerfiles = dataPerfiles.map(cliente => {
        return `<option value="${cliente.id}">${cliente.nombre}</option>`;
    }).join('');
    const { value: formValues, isConfirmed } = await Swal.fire({
        title: 'Ingreso de nuevo perfil',
        html: `
            <div class="input-group mb-3">
                <select id="profile" name="profile" class="form-select">
                    <option value="" disabled selected>Selecciona un perfil</option>
                    ${opcionesPerfiles}
                </select>
            </div>

            <div class="input-group mb-3">
                <select class="form-select" id="permission1">
                    <option value="0" disabled selected>Permiso 1</option>
                    <option value="S">Ver</option>
                    <option value="I">Agregar</option>
                    <option value="U">Editar</option>
                    <option value="D">Eliminar</option>
                </select>

                <select class="form-select" id="permission2">
                    <option value="0" disabled selected>Permiso 2</option>
                    <option value="S">Ver</option>
                    <option value="I">Agregar</option>
                    <option value="U">Editar</option>
                    <option value="D">Eliminar</option>
                </select>

                <select class="form-select" id="permission3">
                    <option value="0" disabled selected>Permiso 3</option>
                    <option value="S">Ver</option>
                    <option value="I">Agregar</option>
                    <option value="U">Editar</option>
                    <option value="D">Eliminar</option>
                </select>

                <select class="form-select" id="permission4">
                    <option value="0" disabled selected>Permiso 4</option>
                    <option value="S">Ver</option>
                    <option value="I">Agregar</option>
                    <option value="U">Editar</option>
                    <option value="D">Eliminar</option>
                </select>
            </div>
        `,
        allowOutsideClick: false,
        focusConfirm: false,
        showCloseButton: true,
        showCancelButton: false,
        confirmButtonText: 'Enviar',
        preConfirm: () => {
            const profile = document.getElementById('profile').value;

            const permission1 = document.getElementById('permission1').value;
            const permission2 = document.getElementById('permission2').value;
            const permission3 = document.getElementById('permission3').value;
            const permission4 = document.getElementById('permission4').value;

            // Validación básica para asegurarse de que no estén vacíos
            if (!profile) {
                Swal.showValidationMessage('Por favor, selecciona el perfil.');
                return false;
            }

            // Verificar si al menos uno de los permisos no está vacío
            if (!profile || ![permission1, permission2, permission3, permission4].some(value => value)) {
                Swal.showValidationMessage('Por favor, selecciona al menos un permiso');
                return false;
            }

            return {
                profile: profile,
                permissions: [permission1, permission2, permission3, permission4].filter(value => value)
            };
        }
    });

    if (isConfirmed) {
        Swal.fire({
            title: 'Validando...',
            text: 'Por favor, espere mientras creamos el perfil.',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });

        fetch('/perfil', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formValues)
        })
            .then(response => response.json())
            .then(data => {
                Swal.close();

                if (data.code === 200) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Correcto',
                        text: data.msge
                    }).then(() => {
                        window.location.href = '/perfil';
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.msge
                    });
                }
            })
            .catch(error => {
                Swal.close();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: error
                });
                console.error('Error:', error);
            });
    } else {
        console.log('Formulario cancelado');
    }
}
