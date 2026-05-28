import os
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

def main(global_config, **settings):
    # Configurar una clave secreta para firmar las cookies de sesión
    session_factory = SignedCookieSessionFactory('clave_secreta_pokedex_123')

    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'frontend', 'static')
    
    config.add_static_view(name='static', path=static_dir)
    
    config.include('.routes')
    config.scan('.views')
    
    return config.make_wsgi_app()