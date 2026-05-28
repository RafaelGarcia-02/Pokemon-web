def init_database():
    print("Inicializando base de datos de la Pokedex...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Crear el Administrador (Maneja el CRUD)
        admin = User(
            username="admin", 
            email="admin@gmail.com", 
            full_name="Ash Ketchum", 
            password_hash="admin",
            role="admin"  # <-- Rol Admin
        )
        
        # 2. Crear el Usuario Normal (Verá la Pokedex)
        user = User(
            username="brock_user", 
            email="brock@pewter.com", 
            full_name="Brock Harrison", 
            password_hash="onix123",
            role="user"   # <-- Rol Regular
        )
        
        db.add(admin)
        db.add(user)
        db.commit()
        print("¡Usuarios 'ash_admin' y 'brock_user' creados con éxito!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()