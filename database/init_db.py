import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Base, engine, SessionLocal, User, Type, TypeMatchup, Pokemon

def init_database():
    print("Reseteando Base de Datos de la Pokédex...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Crear Usuarios base
        admin = User(username="admin", email="admin@gmail.com", full_name="Ash Ketchum", password_hash="admin", role="admin")
        user = User(username="brock_user", email="brock@pewter.com", full_name="Brock Harrison", password_hash="onix123", role="user")
        db.add_all([admin, user])
        db.commit()

        # 2. Crear los 18 Tipos Oficiales
        type_names = ["Acero", "Agua", "Bicho", "Dragón", "Eléctrico", "Fantasma", 
                      "Fuego", "Hada", "Hielo", "Lucha", "Normal", "Planta", 
                      "Psíquico", "Roca", "Siniestro", "Tierra", "Veneno", "Volador"]
        
        type_objs = {}
        for name in type_names:
            t = Type(name=name)
            db.add(t)
            type_objs[name] = t
        db.commit() # Guardamos para generar sus IDs

        # 3. Mapear algunas de las debilidades y fortalezas oficiales más icónicas
        # Estructura: (Atacante, Defensor, Multiplicador)
        relations = [
            # Triángulo inicial
            ("Fuego", "Planta", 2.0), ("Fuego", "Agua", 0.5), ("Fuego", "Fuego", 0.5),
            ("Agua", "Fuego", 2.0), ("Agua", "Planta", 0.5), ("Agua", "Agua", 0.5),
            ("Planta", "Agua", 2.0), ("Planta", "Fuego", 0.5), ("Planta", "Planta", 0.5),
            # Eléctrico y Tierra
            ("Eléctrico", "Agua", 2.0), ("Eléctrico", "Tierra", 0.0), ("Tierra", "Eléctrico", 2.0),
            # Inmunidades clásicas
            ("Normal", "Fantasma", 0.0), ("Fantasma", "Normal", 0.0), ("Lucha", "Fantasma", 0.0)
        ]

        for att_name, def_name, mult in relations:
            matchup = TypeMatchup(
                attacker_id=type_objs[att_name].id,
                defender_id=type_objs[def_name].id,
                multiplier=mult
            )
            db.add(matchup)
        db.commit()

        # 4. Crear los Pokémon iniciales apuntando a sus respectivos IDs de tipo
        p1 = Pokemon(
            pokedex_number=1, name="Bulbasaur", 
            type1_id=type_objs["Planta"].id, type2_id=type_objs["Veneno"].id, 
            hp=45, attack=49, defense=49, 
            image_url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png"
        )
        p2 = Pokemon(
            pokedex_number=4, name="Charmander", 
            type1_id=type_objs["Fuego"].id, type2_id=None, 
            hp=39, attack=52, defense=43, 
            image_url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png"
        )
        p3 = Pokemon(
            pokedex_number=7, name="Squirtle", 
            type1_id=type_objs["Agua"].id, type2_id=None, 
            hp=44, attack=48, defense=65, 
            image_url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png"
        )
        
        db.add_all([p1, p2, p3])
        db.commit()
        print("¡Base de datos e inmunidades oficiales de Pokémon cargadas con éxito!")

    except Exception as e:
        print(f"Error al inicializar: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()