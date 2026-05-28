import os
from dotenv import load_dotenv
from waitress import serve
from backend import main

if __name__ == '__main__':
    load_dotenv()
    
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('SERVER_PORT', 6543))
    
    # Configuraciones básicas para Pyramid
    settings = {
        'pyramid.reload_templates': os.getenv('DEBUG', 'true').lower() == 'true',
        'pyramid.includes': 'pyramid_jinja2'
    }
    
    # Creamos la app WSGI usando nuestra función main en backend
    app = main({}, **settings)
    
    print(f"Iniciando servidor Waitress en http://{host}:{port}")
    serve(app, host=host, port=port)
