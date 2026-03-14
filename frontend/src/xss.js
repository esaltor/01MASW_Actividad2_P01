// Funcion que envia los datos del formulario al backend utilizando fetch
// el endpoint es localhost:8000/asistencia y el metodo es POST
// El body de la peticion es un JSON con los campos nombre y comentario

function enviarAsistencia() {
    const nombre = document.getElementById("name").value;
    const comentario = document.getElementById("comment").value;
    // Crear un objeto con los datos del formulario
    const data = {
        nombre: nombre,
        comentario: comentario
    };
    // Enviar los datos al backend utilizando fetch
    fetch("http://localhost:8000/asistencia", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)  
    })
    .then(response => {
        if (response.ok) {
            response.json().then(data => {
                console.log("Asistencia enviada correctamente:", data);
            });
        } else {
            console.error("Error en la respuesta del servidor");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function obtenerAsistencias() {
    fetch('http://localhost:8000/asistencias')
        .then(response => response.json())
        .then(data => {
            const asistenciasList = document.getElementById('asistenciasList');
            asistenciasList.innerHTML = ''; // Limpiar el contenido previo
            data.asistencias.forEach(asistencia => {
                // Crear nuevos elementos para cada asistencia y agregar a la tabla
                const row = document.createElement('tr');
                const nameCell = document.createElement('td');
                const commentCell = document.createElement('td');
                nameCell.textContent = asistencia.nombre;
                commentCell.textContent = asistencia.comentario;
                row.appendChild(nameCell);
                row.appendChild(commentCell);
                asistenciasList.appendChild(row);   
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Crea una funcion denominada guardarAnuncio que recoja los datos de 
// un formulario con los campos titulo, descripcion, precio y vendedor, 
// y los envie al backend utilizando fetch al endpoint localhost:8000/anuncio con el metodo POST
function guardarAnuncio(e) {
    e.preventDefault();
    const titulo = document.getElementById("titulo").value;
    const descripcion = document.getElementById("descripcion").value;
    const precio = parseFloat(document.getElementById("precio").value);
    const vendedor = document.getElementById("vendedor").value;
    const data = {
        titulo: titulo,
        descripcion: descripcion,
        precio: precio,
        vendedor: vendedor
    };
    fetch("http://localhost:8000/anuncio", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            response.json().then(data => {
                console.log("Anuncio guardado correctamente:", data);
            });

            // Limpiar el formulario después de enviar los datos
            document.getElementById("productForm").reset();

            // Actualizar la lista de anuncios después de guardar uno nuevo
            obtenerAnuncios();
        } else {
            console.error("Error en la respuesta del servidor");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function obtenerAnuncios() {
    fetch('http://localhost:8000/anuncios')
        .then(response => response.json())
        .then(data => {
            const anunciosList = document.getElementById('anunciosList');
            anunciosList.innerHTML = ''; // Limpiar el contenido previo
            data.anuncios.forEach(anuncio => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <h3>${anuncio.titulo}</h3>
                    <p>${anuncio.descripcion}</p>
                    <p>Precio: ${anuncio.precio}</p>
                    <p>Vendedor: ${anuncio.vendedor}</p>
                `;
                anunciosList.appendChild(listItem);
            }); 
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Crea una funcion denominada obtenerAnuncios que haga una peticion GET
// al endpoint localhost:8000/anuncios y muestre los anuncios en una lista con el formato "Titulo: descripcion - precio (vendedor)"
function obtenerAnuncios_validado() {
    fetch('http://localhost:8000/anuncios')
        .then(response => response.json())
        .then(data => {
            const anunciosList = document.getElementById('anunciosList');
            anunciosList.innerHTML = ''; // Limpiar el contenido previo
            data.anuncios.forEach(anuncio => {
                const listItem = document.createElement('li');
                listItem.textContent = `
                    ${anuncio.titulo}: ${anuncio.descripcion} - ${anuncio.precio}€ (${anuncio.vendedor})
                `;
                anunciosList.appendChild(listItem);
            }); 
        })
        .catch(error => {
            console.error('Error:', error);
        });
}