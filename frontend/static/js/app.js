document.addEventListener("DOMContentLoaded", function() {
    // Llamar a nuestro propio endpoint API de posts
    fetch('/api/posts')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('api-data');
            if(data.length === 0) {
                container.innerHTML = "<p>No hay posts disponibles.</p>";
                return;
            }
            let html = '<ul>';
            data.forEach(post => {
                html += `<li><strong>${post.title}</strong>: ${post.content}</li>`;
            });
            html += '</ul>';
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('api-data').innerText = 'Error al cargar los datos del API.';
        });
});
