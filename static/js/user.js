function validarRut(rut) {
    rut = rut.replace(/\./g, '').replace('-', '');

    if (!/^\d{7,8}[0-9Kk]$/.test(rut)) {
        return false;
    }

    const cuerpo = rut.slice(0, -1);
    const dv = rut.slice(-1).toUpperCase();

    let suma = 0;
    let multiplo = 2;

    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += multiplo * parseInt(cuerpo.charAt(i), 10);
        multiplo = multiplo === 7 ? 2 : multiplo + 1;
    }

    const dv_calculado = 11 - (suma % 11);
    const dv_calculado_char = dv_calculado === 11 ? '0' : dv_calculado === 10 ? 'K' : dv_calculado.toString();

    return dv === dv_calculado_char;
}

function validarPassword(password) {
    const isAlphanumeric = /[a-zA-Z]/.test(password) && /\d/.test(password);
    const hasNumbers = (password.match(/\d/g) || []).length >= 4;
    const hasSpecialChar = /[.@]/.test(password);
    return isAlphanumeric && hasNumbers && hasSpecialChar;
}

function separarRutDv(rutCompleto) {
    const rutLimpio = rutCompleto.replace(/\./g, '').toUpperCase();
    const regex = /^(\d{1,8})[-]?([0-9K])$/;
    const resultado = rutLimpio.match(regex);

    if (resultado) {
        return {
            rut: resultado[1], 
            dv: resultado[2]
        };
    } else {
        return {
            rut: '',
            dv: ''
        };
    }
}

async function mostrarAlerta() {
    const { value: formValues, isConfirmed } = await Swal.fire({
        title: 'Ingreso de nuevo usuario',
        html: `
            <div class="input-group mb-3">
                <input type="text" id="rut" class="form-control" placeholder="Rut">
                <div class="input-group-text">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368">
                        <path d="M560-440h200v-80H560v80Zm0-120h200v-80H560v80ZM200-320h320v-22q0-45-44-71.5T360-440q-72 0-116 26.5T200-342v22Zm160-160q33 0 56.5-23.5T440-560q0-33-23.5-56.5T360-640q-33 0-56.5 23.5T280-560q0 33 23.5 56.5T360-480ZM160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm0-80h640v-480H160v480Zm0 0v-480 480Z"/>
                    </svg>
                </div>
            </div>

            <div class="input-group mb-3">
            <input type="text" id="user"  name="user" class="form-control" placeholder="Usuario">
            <div class="input-group-text">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368">
                        <path d="M234-276q51-39 114-61.5T480-360q69 0 132 22.5T726-276q35-41 54.5-93T800-480q0-133-93.5-226.5T480-800q-133 0-226.5 93.5T160-480q0 59 19.5 111t54.5 93Zm246-164q-59 0-99.5-40.5T340-580q0-59 40.5-99.5T480-720q59 0 99.5 40.5T620-580q0 59-40.5 99.5T480-440Zm0 360q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q53 0 100-15.5t86-44.5q-39-29-86-44.5T480-280q-53 0-100 15.5T294-220q39 29 86 44.5T480-160Zm0-360q26 0 43-17t17-43q0-26-17-43t-43-17q-26 0-43 17t-17 43q0 26 17 43t43 17Zm0-60Zm0 360Z"/>
                    </svg>
                </div>
            </div>

            <div class="input-group mb-3">
            <input type="password" id="pswrd" name="pswrd" class="form-control" placeholder="Password">
            <div class="input-group-text">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368">
                        <path d="M80-200v-80h800v80H80Zm46-242-52-30 34-60H40v-60h68l-34-58 52-30 34 58 34-58 52 30-34 58h68v60h-68l34 60-52 30-34-60-34 60Zm320 0-52-30 34-60h-68v-60h68l-34-58 52-30 34 58 34-58 52 30-34 58h68v60h-68l34 60-52 30-34-60-34 60Zm320 0-52-30 34-60h-68v-60h68l-34-58 52-30 34 58 34-58 52 30-34 58h68v60h-68l34 60-52 30-34-60-34 60Z"/>
                    </svg>
                </div>
            </div>

            <div class="input-group mb-3">
            <input type="text" id="nombres" name="nombres" class="form-control" placeholder="Nombres">
            <div class="input-group-text">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368">
                        <path d="M234-276q51-39 114-61.5T480-360q69 0 132 22.5T726-276q35-41 54.5-93T800-480q0-133-93.5-226.5T480-800q-133 0-226.5 93.5T160-480q0 59 19.5 111t54.5 93Zm246-164q-59 0-99.5-40.5T340-580q0-59 40.5-99.5T480-720q59 0 99.5 40.5T620-580q0 59-40.5 99.5T480-440Zm0 360q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q53 0 100-15.5t86-44.5q-39-29-86-44.5T480-280q-53 0-100 15.5T294-220q39 29 86 44.5T480-160Zm0-360q26 0 43-17t17-43q0-26-17-43t-43-17q-26 0-43 17t-17 43q0 26 17 43t43 17Zm0-60Zm0 360Z"/>
                    </svg>
                </div>
            </div>

            <div class="input-group mb-3">
            <input type="text" id="ap_pat" name="ap_pat" class="form-control" placeholder="Apellido Paterno">
            <div class="input-group-text">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368">
                        <path d="M234-276q51-39 114-61.5T480-360q69 0 132 22.5T726-276q35-41 54.5-93T800-480q0-133-93.5-226.5T480-800q-133 0-226.5 93.5T160-480q0 59 19.5 111t54.5 93Zm246-164q-59 0-99.5-40.5T340-580q0-59 40.5-99.5T480-720q59 0 99.5 40.5T620-580q0 59-40.5 99.5T480-440Zm0 360q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q53 0 100-15.5t86-44.5q-39-29-86-44.5T480-280q-53 0-100 15.5T294-220q39 29 86 44.5T480-160Zm0-360q26 0 43-17t17-43q0-26-17-43t-43-17q-26 0-43 17t-17 43q0 26 17 43t43 17Zm0-60Zm0 360Z"/>
                    </svg>
                </div>
            </div>

            <div class="input-group mb-3">
            <input type="text" id="ap_mat" name="ap_mat" class="form-control" placeholder="Apellido Materno">
            <div class="input-group-text">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368">
                        <path d="M234-276q51-39 114-61.5T480-360q69 0 132 22.5T726-276q35-41 54.5-93T800-480q0-133-93.5-226.5T480-800q-133 0-226.5 93.5T160-480q0 59 19.5 111t54.5 93Zm246-164q-59 0-99.5-40.5T340-580q0-59 40.5-99.5T480-720q59 0 99.5 40.5T620-580q0 59-40.5 99.5T480-440Zm0 360q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q53 0 100-15.5t86-44.5q-39-29-86-44.5T480-280q-53 0-100 15.5T294-220q39 29 86 44.5T480-160Zm0-360q26 0 43-17t17-43q0-26-17-43t-43-17q-26 0-43 17t-17 43q0 26 17 43t43 17Zm0-60Zm0 360Z"/>
                    </svg>
                </div>
            </div>

            <div class="input-group mb-3">
                <select id="perfil" name="perfil" class="form-select">
                    <option value="" disabled selected>Selecciona un perfil</option>
                    <option value="Administrador">Administrador</option>
                    <option value="Técnico">Técnico</option>
                    <option value="Supervisor">Supervisor</option>
                </select>
                <div class="input-group-text">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368">
                        <path d="M412-168q45-91 120-121.5T660-320q23 0 45 4t43 10q24-38 38-82t14-92q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 45 11.5 86t34.5 76q41-20 85-31t89-11q32 0 61.5 5.5T500-340q-23 12-43.5 28T418-278q-12-2-20.5-2H380q-32 0-63.5 7T256-252q32 32 71.5 53.5T412-168Zm68 88q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80ZM380-420q-58 0-99-41t-41-99q0-58 41-99t99-41q58 0 99 41t41 99q0 58-41 99t-99 41Zm0-80q25 0 42.5-17.5T440-560q0-25-17.5-42.5T380-620q-25 0-42.5 17.5T320-560q0 25 17.5 42.5T380-500Zm280 120q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM480-480Z"/>
                    </svg>
                </div>
            </div>

        `,
        allowOutsideClick: false,
        focusConfirm: false,
        showCloseButton: true,
        showCancelButton: false,
        confirmButtonText: 'Enviar',
        preConfirm: () => {
            const rutCompleto = document.getElementById('rut').value;
            const { rut, dv } = separarRutDv(rutCompleto);
            const user = document.getElementById('user').value;
            const pswrd = document.getElementById('pswrd').value;
            const nombres = document.getElementById('nombres').value;
            const ap_pat = document.getElementById('ap_pat').value;
            const ap_mat = document.getElementById('ap_mat').value;
            const perfil = document.getElementById('perfil').value;

            // Validación básica para asegurarse de que no estén vacíos
            if (!rutCompleto || !user || !pswrd || !nombres || !ap_pat || !ap_mat || !perfil) {
                Swal.showValidationMessage('Por favor, completa todos los campos');
                return false;
            } 

            // Validar el RUT
            if (!validarRut(rutCompleto)) {
                Swal.showValidationMessage('Rut inválido');
                return false;
            }

            // Validar la pswrd
            if (!validarPassword(pswrd)) {
                Swal.showValidationMessage(
                    'La contraseña debe ser alfanumérica, contener al menos 4 números y al menos un punto (.) o arroba (@)');
                return false;
            }

            return {
                rut: rut,
                dv: dv,
                user: user,
                pswrd: pswrd,
                nombres: nombres,
                ap_pat: ap_pat,
                ap_mat: ap_mat,
                perfil: perfil
            };
        }
    });

    if (isConfirmed) {
        Swal.fire({
            title: 'Validando...',
            text: 'Por favor, espere mientras creamos al usuario.',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });

        fetch('/usuario', {
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
                        window.location.href = '/usuario';
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
