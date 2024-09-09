

// document.getElementById('formato').addEventListener('change', function () {
//     var selectedValue = this.value;
//     var separatorDiv = document.getElementById('formato-seleccionado');

//     if (selectedValue != 0) {
//         separatorDiv.classList.remove('hidden');
//     } else {
//         separatorDiv.classList.add('hidden');
//     }
// });

// document.getElementById('formato-seleccionado').addEventListener('change', function () {
//     var selectedValue = this.value;
//     var separatorDiv = document.getElementById('archivo');

//     if (selectedValue != 0) {
//         separatorDiv.classList.remove('hidden');
//     } else {
//         separatorDiv.classList.add('hidden');
//     }
// });

// document.getElementById('file').addEventListener('change', function () {
//     var selectedValue = this.value;
//     var separatorDiv = document.getElementById('btn');

//     if (selectedValue != 0) {
//         separatorDiv.classList.remove('hidden');

//         const formato = document.getElementById('formato').value;
//         const separador = document.getElementById('separador').value;
//         const file = document.getElementById('file').value;

//         // Asegúrate de que los valores son válidos
//         if (formato && separador && file) {
//             const formValues = {
//                 formato: formato,
//                 separador: separador,
//                 file: file
//             };

//             

//     } else {
//         separatorDiv.classList.add('hidden');
//     }
// });


document.getElementById('formato').addEventListener('change', function () {
    var selectedValue = this.value;
    var separatorDiv = document.getElementById('formato-seleccionado');

    // Mostrar el selector de separador solo si el formato no es "0"
    if (selectedValue !== '0') {
        separatorDiv.classList.remove('hidden');
    } else {
        separatorDiv.classList.add('hidden');
    }
});

document.getElementById('separador').addEventListener('change', function () {
    var selectedValue = this.value;
    var fileDiv = document.getElementById('archivo');

    // Mostrar el input de archivo si se selecciona un separador válido
    if (selectedValue !== '0') {
        fileDiv.classList.remove('hidden');
    } else {
        fileDiv.classList.add('hidden');
    }
});

document.getElementById('file').addEventListener('change', function () {
    var btnDiv = document.getElementById('btn');
    var file = this.files[0];  // Verificar si un archivo ha sido seleccionado

    // Mostrar el botón de enviar solo si un archivo ha sido seleccionado
    if (file) {
        btnDiv.classList.remove('hidden');
    } else {
        btnDiv.classList.add('hidden');
    }
});

function load() {
    const formato = document.getElementById('formato').value;
    const separador = document.getElementById('separador').value;
    const file = document.getElementById('file').files[0];

    if (formato && separador && file) {
        const formData = new FormData();
        formData.append('formato', formato);
        formData.append('separador', separador);
        formData.append('file', file);

        Swal.fire({
            title: 'Cargando...',
            text: 'Por favor espera',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        fetch('/cliente/masivo', {
            method: 'POST',
            body: formData
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
                    window.location.href = '/cliente';
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
            Swal.fire({
                icon: 'error',
                title: 'Error en el servidor',
                text: error.message
            });
        });

        return false;  // Evitar que el formulario se envíe de manera predeterminada
    } else {
        Swal.fire({
            icon: 'warning',
            title: 'Datos incompletos',
            text: 'Por favor, llena todos los campos antes de enviar'
        });
        return false;  // Evitar que el formulario se envíe si los datos no están completos
    }
}




// // // // // function load() {
// // // // //     fetch('/cliente/masivo', {
// // // // //         method: 'POST',
// // // // //         headers: {
// // // // //             'Content-Type': 'application/json'
// // // // //         },
// // // // //         body: JSON.stringify(formValues)
// // // // //     })
// // // // //         .then(response => response.json())
// // // // //         .then(data => {
// // // // //             Swal.close();

// // // // //             if (data.code === 200) {
// // // // //                 Swal.fire({
// // // // //                     icon: 'success',
// // // // //                     title: 'Correcto',
// // // // //                     text: data.msge
// // // // //                 }).then(() => {
// // // // //                     window.location.href = '/cliente';
// // // // //                 });
// // // // //             } else {
// // // // //                 Swal.fire({
// // // // //                     icon: 'error',
// // // // //                     title: 'Error',
// // // // //                     text: data.msge
// // // // //                 });
// // // // //             }
// // // // //         })
// // // // //         .catch(error => {
// // // // //             Swal.close();
// // // // //             Swal.fire({
// // // // //                 icon: 'error',
// // // // //                 title: 'Error',
// // // // //                 text: error
// // // // //             });
// // // // //             console.error('Error:', error);
// // // // //         });
// // // // // }





