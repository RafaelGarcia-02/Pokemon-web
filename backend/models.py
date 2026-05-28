import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    password_hash = Column(String(255))
    role = Column(String(20), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==========================================
# NUEVO MODELO: POKEMON
# ==========================================
class Type (Base):
    __tablename__ = 'types'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    matchups = relationship("TypeMatchup", foreign_keys="[TypeMatchup.attacker_id]", back_populates="attacker")

class TypeMatchup(Base):
    __tablename__ = 'type_matchups'
    id = Column(Integer, primary_key=True)
    attacker_id = Column(Integer, ForeignKey('types.id'), nullable=False)
    defender_id = Column(Integer, ForeignKey('types.id'), nullable=False)
    multiplier = Column(Float, nullable=False, default=1.0) # <-- ¡Aquí ya no fallará!

    attacker = relationship("Type", foreign_keys=[attacker_id], back_populates="matchups")
    defender = relationship("Type", foreign_keys=[defender_id])
class Pokemon(Base):
    __tablename__ = 'pokemons'
    id = Column(Integer, primary_key=True)
    pokedex_number = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    
    # Claves foráneas hacia la tabla de tipos
    type1_id = Column(Integer, ForeignKey('types.id'), nullable=False)
    type2_id = Column(Integer, ForeignKey('types.id'), nullable=True)
    
    hp = Column(Integer, default=50)
    attack = Column(Integer, default=50)
    defense = Column(Integer, default=50)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones de SQLAlchemy para extraer los nombres cómodamente
    t1 = relationship("Type", foreign_keys=[type1_id])
    t2 = relationship("Type", foreign_keys=[type2_id])