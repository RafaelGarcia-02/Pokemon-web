def includeme(config):
    # Autenticación
    config.add_route('login', '/login')
    config.add_route('register', '/register')
    config.add_route('logout', '/logout')

    # Vistas de Roles
    config.add_route('home', '/')
    config.add_route('admin_view', '/admin')
    config.add_route('user_view', '/dashboard')
    
    # API GENERAL
    config.add_route('api_health', '/api/health')
    config.add_route('api_users', '/api/users')
    
    # API POKÉMON (CRUD)
    config.add_route('api_types', '/api/types')
    config.add_route('api_pokemons', '/api/pokemons') 
    config.add_route('api_pokemon_id', '/api/pokemons/{id}')