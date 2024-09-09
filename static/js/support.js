function mostrarAlertaSupport() {
    const opcionesClientes = dataClientes.map(cliente => {
        return `<option value="${cliente.id}">${cliente.nombre}</option>`;
    }).join('');

    let opcionesSitios = dataSitios.map(sitio => {
        return `<option value="${sitio.id}" data-cliente-id="${sitio.cliente_id}">${sitio.nombre}</option>`;
    }).join('');

    const opcionesTecnicos = dataTecnicos.map(tecnico => {
        return `<option value="${tecnico.id}">${tecnico.nombre}</option>`;
    }).join('');

    Swal.fire({
        title: "Ingreso de nuevo soporte",
        html: `
            <div class="input-group mb-3">
                <select id="client" name="client" class="form-select">
                    <option value="" disabled selected>Selecciona un cliente</option>
                    ${opcionesClientes}
                </select>
            </div>

            <div class="input-group mb-3">
                <select id="site" name="site" class="form-select">
                    <option value="" disabled selected>Selecciona un sitio</option>
                </select>
            </div>

            <div class="input-group mb-3">
                <select id="technicians" name="technicians" class="form-select">
                    <option value="" disabled selected>Selecciona un técnico</option>
                    ${opcionesTecnicos}
                </select>
            </div>

            <div class="input-group mb-3">
                <textarea name="equipment_details" id="equipment_details" class="form-control" placeholder="Detalle de equipos a revisar"></textarea>
            </div>

            <div class="input-group mb-3">
                <textarea name="jobs_details" id="jobs_details" class="form-control" placeholder="Detalle de trabajos realizados"></textarea>
            </div>

            <div class="input-group mb-3">
                <label class="form-control">Hora Inicio</label>
                <input type="time" id="date_start" name="date_start" class="form-control">
            </div>

            <div class="input-group mb-3">
                <label class="form-control">Hora Termino</label>
                <input type="time" id="date_end" name="date_end" class="form-control">
            </div>

            <div class="input-group mb-3">
                <input type="text" id="validator" name="validator" class="form-control" placeholder="Quien Valida">
            </div>

            <div class="input-group mb-3">
                <input type="file" class="form-control" id="file" name="file" multiple>
            </div>
        `,
        allowOutsideClick: false,
        focusConfirm: false,
        showCloseButton: true,
        confirmButtonText: 'Finalizar',
        didOpen: () => {
            const clientSelect = document.getElementById('client');
            const siteSelect = document.getElementById('site');

            siteSelect.innerHTML = '<option value="" disabled selected>Selecciona un sitio</option>';

            clientSelect.addEventListener('change', () => {
                const clienteId = clientSelect.value;

                if (!clienteId) {
                    siteSelect.innerHTML = '<option value="" disabled selected>Selecciona un sitio</option>';
                    return;
                }

                const sitiosFiltrados = dataSitios.filter(sitio => sitio.cliente_id == clienteId);

                siteSelect.innerHTML = '<option value="" disabled selected>Selecciona un sitio</option>' + sitiosFiltrados.map(sitio => {
                    return `<option value="${sitio.id}">${sitio.nombre}</option>`;
                }).join('');
            });
        },
        preConfirm: () => {
            const client = document.getElementById('client').value;
            const site = document.getElementById('site').value;
            const technicians = document.getElementById('technicians').value;
            const equipment_details = document.getElementById('equipment_details').value;
            const jobs_details = document.getElementById('jobs_details').value;
            const date_start = document.getElementById('date_start').value;
            const date_end = document.getElementById('date_end').value;
            const fileInput = document.getElementById('file');
            const validator = document.getElementById('validator').value;

            if (!client || !site || !technicians || !equipment_details || !jobs_details || !date_start || !date_end) {
                Swal.showValidationMessage('Por favor, completa todos los campos.');
                return false;
            }

            var files = fileInput.files;

            if (files.length === 0) {
                Swal.showValidationMessage('Sube al menos una evidencia fotográfica.');
                return false;
            }

            // Validar cada archivo
            for (const file of files) {
                const fileName = file.name;
                const fileExtension = fileName.split('.').pop().toLowerCase();
                const validExtensions = ['jpg', 'jpeg', 'png'];
                const fileType = file.type;
                const validMimeTypes = ['image/jpeg', 'image/png', 'image/jpg'];

                if (!validExtensions.includes(fileExtension) && !validMimeTypes.includes(fileType)) {
                    Swal.showValidationMessage("Por favor, selecciona imágenes válidas (jpg, jpeg, png).");
                    return false;
                }
            }

            // Crear un nuevo FormData
            const formData = new FormData();
            formData.append('client', client);
            formData.append('site', site);
            formData.append('technicians', technicians);
            formData.append('equipment_details', equipment_details);
            formData.append('jobs_details', jobs_details);
            formData.append('validator', validator);
            formData.append('date_start', date_start);
            formData.append('date_end', date_end);

            // Agregar todos los archivos seleccionados
            for (const file of files) {
                formData.append('files[]', file); // 'files[]' permite enviar múltiples archivos en un solo campo
            }

            return formData;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: 'Cargando...',
                text: 'Estamos finalizando el formulario',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            fetch('/soporte', {
                method: 'POST',
                body: result.value
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
                            window.location.href = '/soporte';
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
                        title: 'Error en el servidor',
                        text: error.message
                    });
                });
        }
    });
}
