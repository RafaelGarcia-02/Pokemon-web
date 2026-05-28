import os
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound
from .models import SessionLocal, User, Pokemon , Type

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================================
# 1. VISTAS DEL FRONTEND (Páginas Web)
# ==========================================

@view_config(route_name='home')
def home_view(request):
    session = request.session
    if 'username' in session:
        if session.get('role') == 'admin':
            return HTTPFound(location='/admin')
        return HTTPFound(location='/dashboard')
    return HTTPFound(location='/login')

LOGIN_TEMPLATE = os.path.join(BASE_DIR, 'frontend', 'templates', 'login.html')
@view_config(route_name='login', renderer=LOGIN_TEMPLATE)
def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.params.get('username')
        password = request.params.get('password')
        
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()
        
        if user and user.password_hash == password:
            request.session['username'] = user.username
            request.session['role'] = user.role
            request.session['full_name'] = user.full_name
            
            if user.role == 'admin':
                return HTTPFound(location='/admin')
            return HTTPFound(location='/dashboard')
        else:
            error_message = "Usuario o contraseña incorrectos."
    return {'error': error_message}

REGISTER_TEMPLATE = os.path.join(BASE_DIR, 'frontend', 'templates', 'register.html')
@view_config(route_name='register', renderer=REGISTER_TEMPLATE)
def register_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.params.get('username')
        email = request.params.get('email')
        full_name = request.params.get('full_name')
        password = request.params.get('password')
        
        db = SessionLocal()
        existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
        
        if existing:
            error_message = "El nombre de usuario o email ya están registrados."
            db.close()
        else:
            new_user = User(username=username, email=email, full_name=full_name, password_hash=password, role='user')
            db.add(new_user)
            db.commit()
            db.close()
            return HTTPFound(location='/login')
    return {'error': error_message}

@view_config(route_name='logout')
def logout_view(request):
    request.session.invalidate()
    return HTTPFound(location='/login')

ADMIN_TEMPLATE = os.path.join(BASE_DIR, 'frontend', 'templates', 'admin.html')
@view_config(route_name='admin_view', renderer=ADMIN_TEMPLATE)
def admin_view(request):
    if request.session.get('role') != 'admin':
        return HTTPFound(location='/login')
    return {'admin_name': request.session.get('full_name')}

USER_TEMPLATE = os.path.join(BASE_DIR, 'frontend', 'templates', 'user.html')
@view_config(route_name='user_view', renderer=USER_TEMPLATE)
def user_view(request):
    if 'username' not in request.session:
        return HTTPFound(location='/login')
    return {'user_name': request.session.get('full_name')}


# ==========================================
# 2. VISTAS DE LA API (Endpoints JSON)
# ==========================================

@view_config(route_name='api_health', renderer='json')
def health_check(request):
    return {"status": "healthy"}

# --- CRUD POKÉMON ---@view_config(route_name='api_types', request_method='GET', renderer='json')
@view_config(route_name='api_types', request_method='GET', renderer='json')
def get_types(request):
    db = SessionLocal()
    try:
        types = db.query(Type).order_by(Type.name).all()
        result = [{"id": t.id, "name": t.name} for t in types]
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


# GET /api/pokemons -> Leer todos los Pokémon
@view_config(route_name='api_pokemons', request_method='GET', renderer='json')
def get_all_pokemons(request):
    # Si no hay sesión activa, devolvemos un diccionario directo (JSON válido) con estado 401 simulado
    if 'username' not in request.session:
        request.response.status_code = 401
        return {"success": False, "error": "No autorizado. Inicie sesión de nuevo."}
        
    db = SessionLocal()
    pokemons = db.query(Pokemon).order_by(Pokemon.pokedex_number).all()
    
    result = []
    for p in pokemons:
        result.append({
            "id": p.id,
            "pokedex_number": p.pokedex_number,
            "name": p.name,
            "type1_id": p.type1_id,
            "type2_id": p.type2_id,
            "type1_name": p.t1.name if p.t1 else "Ninguno",
            "type2_name": p.t2.name if p.t2 else None,
            "hp": p.hp,
            "attack": p.attack,
            "defense": p.defense,
            "image_url": p.image_url
        })
    db.close()
    return result
    return result


# POST /api/pokemons -> Crear Pokémon (Solo Admin)
@view_config(route_name='api_pokemons', request_method='POST', renderer='json')
def create_pokemon(request):
    if request.session.get('role') != 'admin':
        return HTTPForbidden({"error": "No autorizado"})
        
    data = request.json_body
    db = SessionLocal()
    try:
        nuevo_pokemon = Pokemon(
            pokedex_number=int(data['pokedex_number']),
            name=data['name'],
            type1_id=int(data['type1_id']),
            type2_id=int(data['type2_id']) if data.get('type2_id') else None,
            hp=int(data.get('hp', 50)),
            attack=int(data.get('attack', 50)),
            defense=int(data.get('defense', 50)),
            image_url=data.get('image_url')
        )
        db.add(nuevo_pokemon)
        db.commit()
        return {"success": True, "message": f"¡{nuevo_pokemon.name} añadido!"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


# PUT /api/pokemons/{id} -> Editar Pokémon (Solo Admin)
@view_config(route_name='api_pokemon_id', request_method='PUT', renderer='json')
def update_pokemon(request):
    if request.session.get('role') != 'admin':
        return HTTPForbidden({"error": "No autorizado"})
        
    pk_id = request.matchdict['id']
    data = request.json_body
    
    db = SessionLocal()
    pokemon = db.query(Pokemon).filter(Pokemon.id == pk_id).first()
    
    if not pokemon:
        db.close()
        return HTTPNotFound({"error": "No encontrado"})
        
    try:
        pokemon.pokedex_number = int(data['pokedex_number'])
        pokemon.name = data['name']
        pokemon.type1_id = int(data['type1_id'])
        pokemon.type2_id = int(data['type2_id']) if data.get('type2_id') else None
        pokemon.hp = int(data['hp'])
        pokemon.attack = int(data['attack'])
        pokemon.defense = int(data['defense'])
        pokemon.image_url = data.get('image_url')
        
        db.commit()
        return {"success": True, "message": "¡Actualizado correctamente!"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


# DELETE /api/pokemons/{id} -> Borrar Pokémon (Solo Admin)
@view_config(route_name='api_pokemon_id', request_method='DELETE', renderer='json')
def delete_pokemon(request):
    if request.session.get('role') != 'admin':
        return HTTPForbidden({"error": "No autorizado"})
        
    pk_id = request.matchdict['id']
    
    db = SessionLocal()
    pokemon = db.query(Pokemon).filter(Pokemon.id == pk_id).first()
    
    if not pokemon:
        db.close()
        return HTTPNotFound({"error": "Pokémon no encontrado"})
        
    try:
        db.delete(pokemon)
        db.commit()
        return {"success": True, "message": "Pokémon eliminado de la Pokédex."}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()