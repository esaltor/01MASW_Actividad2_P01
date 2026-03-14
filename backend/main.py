from typing import Annotated, Union
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi import Request
from pathlib import Path
from urllib.parse import urlparse
import os
import requests
import socket
import ipaddress
from bs4 import BeautifulSoup
from pydantic import BaseModel
from sqlalchemy import create_engine,text
from sqlmodel import Field, Session, SQLModel, create_engine, select

from fastapi import FastAPI

class Cartel(BaseModel):
    name: str

# Conexion a la base de datos SQLite
DATABASE_URL = "sqlite:///./sql/test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crear un nuevo modelo para representar un usuario
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

# Crear un nuevo modelo para representar una asistencia
class Asistencia(SQLModel, table=True):
    id: int = Field(primary_key=True)
    nombre: str
    comentario: str

# Crear un nuevo modelo para representar un anuncio, con título, 
# descripción, precio y nombre del vendedor
class Anuncio(SQLModel, table=True):
    id: int = Field(primary_key=True)
    titulo: str
    descripcion: str
    precio: float
    vendedor: str

# Crear un nuevo modelo para representar las cookies de un usuario
class Cookie(SQLModel, table=True):
    id: int = Field(primary_key=True)
    nombre: str
    valor: str

# Crear un modelo para representar la petición de login
class LoginRequest(BaseModel):
    username: str
    password: str

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Endpoint GET /carteles que devuelve en formato JSON una lista con los nombres de los archivos
# de la carpeta 'carteles' ubicada en el directorio /carteles del servidor.
# utilizando la clase os y sin comprobar si la carpeta existe o no.
@app.get("/cartelesv2")
def get_carteles():
    carteles_dir = Path("carteles")
    archivos = [archivo.name for archivo in carteles_dir.iterdir() if archivo.is_file()]
    return JSONResponse(content=archivos)   

# Ruta devuelve en un json los nombres de los archivos en el directorio carteles
@app.get("/cartelesv1")
async def list_carteles():
    carteles_dir = "carteles"
    try:
        files = os.listdir(carteles_dir)
        return {"carteles": files}
    except Exception as e:
        return {"error": "Could not list carteles"}


# Ruta que devuelve un cartel a partir de su nombre con método post
# Se valida el nombre del fichero para evitar SSRF
@app.post("/cartelesvalidado")
async def post_cartel(cartel: Cartel):
    # Validar la ruta del archivo
    if ".." in cartel.name or "/" in cartel.name or "\\" in cartel.name:
        return {"error": "Invalid file name"}
    cartel_path = os.path.join("carteles", cartel.name)
    if os.path.isfile(cartel_path):
        return FileResponse(cartel_path)
    else:
        return {"error": "Cartel not found"}
    
# Ruta que devuelve un cartel a partir de su nombre con método post
# No se valida el nombre del fichero para demostrar SSRF
@app.post("/carteles")
async def post_cartel(cartel: Cartel):
    cartel_path = os.path.join("carteles", cartel.name)
    if os.path.isfile(cartel_path):
        return FileResponse(cartel_path)
    else:
        return {"error": "Cartel not found"}

# Endpoint para generar la vista previa de un enlace. Recibe una URL 
# y devuelve un JSON con el título de la página y una imagen de vista previa
# Sin validaciones para demostrar SSRF.
@app.get("/preview")
def preview(url: str):
    response = requests.get(url)

    # Si devuelve HTML intentamos sacar el título
    if "text/html" in response.headers.get("content-type", ""):
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        return {"type": "html", "data": title}

    # Si devuelve JSON lo pasamos tal cual
    if "application/json" in response.headers.get("content-type", ""):
        return {"type": "json", "data": response.json()}

    return {"type": "raw", "data": response.text}

# Endpoint para generar la vista previa de un enlace con validaciones para evitar SSRF.
# Recibe una URL y devuelve un JSON con el título de la página y una imagen de vista previa
@app.get("/previewvalidado")
def preview(url: str):
    parsed = urlparse(url)

    # Validar esquema
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Esquema inválido")

    # Bloquear IPs privadas o localhost
    if is_private(parsed.hostname):
        raise HTTPException(status_code=403, detail="Acceso a red interna prohibido")

    # Solicitar contenido seguro
    response = requests.get(url, timeout=5)

    # Procesar HTML para mostrar título
    if "text/html" in response.headers.get("content-type", ""):
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        return {"type": "html", "data": title}

    # Procesar JSON
    if "application/json" in response.headers.get("content-type", ""):
        return {"type": "json", "data": response.json()}

    # Otros contenidos
    return {"type": "raw", "data": response.text}

# Función para comprobar si un hostname es privado o no utilizando la librería ipaddress y socket
def is_private(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        return ipaddress.ip_address(ip).is_private
    except:
        return True  # Si no se puede resolver, asumimos privada

# Endpoint interno (no expuesto en frontend)
@app.get("/admin")
def admin():
    return {
        "database_password": "SuperSecret123",
        "api_key": "ADMIN-KEY-456",
        "internal_service": "http://10.0.0.5:5000"
    }

# Endpoint de login que recibe un username y password y devuelve un mensaje de éxito o error
@app.post("/login")
async def login(data: LoginRequest):

    try:
        # VULNERABLE: concatenación directa
        query = f"SELECT * FROM users WHERE username = '{data.username}' AND password = '{data.password}'"
        print("QUERY EJECUTADA:", query)

        with engine.connect() as connection:
            result = connection.execute(text(query))
            user = result.mappings().first()

        if user:
            return {
                "message": "Login correcto",
                "user": user["username"],
                "role": user["role"]
            }
        else:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    except Exception as e:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

@app.post("/loginvalidado")
async def loginvalidado(data: LoginRequest):

    # Validación básica
    if not data.username or not data.password:
        raise HTTPException(
            status_code=400,
            detail="Usuario y contraseña son obligatorios"
        )

    try:
        # Consulta parametrizada
        query = text("SELECT * FROM users WHERE username = :username AND password = :password")

        with engine.connect() as connection:
            result = connection.execute(query, {
                "username": data.username,
                "password": data.password
            })
            # Imprimir la consulta ejecutada para demostrar que se ha parametrizado correctamente
            print("QUERY EJECUTADA:", query.compile(compile_kwargs={"literal_binds": True}))

            user = result.mappings().first()
            print("USUARIO ENCONTRADO:", user)

        if user:
            return {
                "message": "Login correcto",
                "user": user["username"],
                "role": user["role"]
            }
        else:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    except Exception as e:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

# Endpoint que devuelva todos los usuarios de la base de datos SQLite
# usando SQLAlchemy y sin validación de entrada para demostrar SQL Injection
@app.get("/users")
async def get_users():
    try:
        query = text("SELECT * FROM user")
        with engine.connect() as connection:
            result = connection.execute(query)
            users = result.mappings().all()
       # Convertir los resultados a una lista de diccionarios
            users_list = [dict(row) for row in users]
            return {"users": users_list}
    except Exception as e:
        return {"error": "Could not fetch users"}
    
# Enoint que devuelva un usuario a partir de su id usando SQLAlchemy
@app.get("/users/{user_id}")
#async def get_user(user_id: int):
async def get_user(user_id: Union[int, str]):
    try:
        #query = text("SELECT * FROM user WHERE id = :user_id")
        #1' OR '1'='1'---
        query = text(f"SELECT * FROM user WHERE id = {user_id}")
        with engine.connect() as connection:
            #result = connection.execute(query, {"user_id": user_id})
            result = connection.execute(query)
            #user = result.mappings().first()
            user = result.mappings().all()
            # Convertir los resultados a una lista de diccionarios
            users_list = [dict(row) for row in user]
            return {"users": users_list}
    except Exception as e:
        return {"error": "Could not fetch user"}
    
# Crea un nuevo endpoint que lea los usuarios desde la base de datos utilizando SQLModel y devuelva el resultado
@app.get("/users_sqlmodel")
async def get_users_sqlmodel(session: SessionDep):
    try:
        users = session.exec(select(User)).all()
        users_list = [user.dict() for user in users]
        return {"users": users_list}
    except Exception as e:
        return {"error": "Could not fetch users"}
    
# Devolver un usuario por su id utilizando SQLModel
@app.get("/user_sqlmodel/{user_id}")
async def get_user_sqlmodel(user_id: int, session: SessionDep):
    try:
        user = session.get(User, user_id)
        if user:
            user_dict = user.dict()
            return {"user": [user_dict]}
        else:
            return {"error": "User not found"}
    except Exception as e:
        return {"error": "Could not fetch user"}
    

# Añadir un nuevo endpoint donde se hace insert con SQLmodel de una nueva asistencia a las base de datos
@app.post("/asistencia")
async def add_asistencia(asistencia: Asistencia, session: SessionDep):
    try:
        nueva_asistencia = Asistencia(nombre=asistencia.nombre, comentario=asistencia.comentario)
        session.add(nueva_asistencia)
        session.commit()
        session.refresh(nueva_asistencia)
        return {"asistencia": nueva_asistencia.dict()}
    except Exception as e:
        return {"error": "Could not add asistencia"}
    

# Añadir un nuevo endpoint donde se liste todas las asistencias de la base de datos utilizando SQLModel
@app.get("/asistencias")
async def get_asistencias(session: SessionDep):
    try:
        asistencias = session.exec(select(Asistencia)).all()
        asistencias_list = [asistencia.dict() for asistencia in asistencias]
        return {"asistencias": asistencias_list}
    except Exception as e:
        return {"error": "Could not fetch asistencias"} 

# Añadir un nuevo endpoint donde se liste todas las asistencias de la base de datos utilizando SQLModel 
# pero se devuelve el resultado en html en lugar de json
@app.get("/asistencias_html")
async def get_asistencias_html(session: SessionDep):
    try:
        asistencias = session.exec(select(Asistencia)).all()
        asistencias_list = [asistencia.dict() for asistencia in asistencias]
        html_content = "<html><body><h1>Asistencias</h1><ul>"
        for asistencia in asistencias_list:
            html_content += f"<li>{asistencia['nombre']}: {asistencia['comentario']}</li>"
        html_content += "</ul></body></html>"
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        return {"error": "Could not fetch asistencias"} 

# Añadir un nuevo endpoint donde se haga insert de un nuevo anuncio 
# a las base de datos utilizando SQLModel
@app.post("/anuncio")
async def add_anuncio(anuncio: Anuncio, session: SessionDep):
    try:
        nuevo_anuncio = Anuncio(titulo=anuncio.titulo, descripcion=anuncio.descripcion, precio=anuncio.precio, vendedor=anuncio.vendedor)
        session.add(nuevo_anuncio)
        session.commit()
        session.refresh(nuevo_anuncio)
        return {"anuncio": nuevo_anuncio.dict()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/anunciovalidado")
async def add_anuncio_validado(anuncio: Anuncio, session: SessionDep):
    try:
        # Escapar todo el texto de usuario
        titulo_seguro = escape_html(anuncio.titulo)
        descripcion_segura = escape_html(anuncio.descripcion)
        vendedor_seguro = escape_html(anuncio.vendedor)

        nuevo_anuncio = Anuncio(
            titulo=titulo_seguro,
            descripcion=descripcion_segura,
            precio=anuncio.precio,
            vendedor=vendedor_seguro
        )

        session.add(nuevo_anuncio)
        session.commit()
        session.refresh(nuevo_anuncio)
        return {"anuncio": nuevo_anuncio.dict()}
    except Exception as e:
        return {"error": str(e)}

def escape_html(texto: str) -> str:
    return (
        texto.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#x27;")
             .replace("/", "&#x2F;")
    )

# Añadir un nuevo endpoint donde se liste todos los anuncios
# de la base de datos utilizando SQLModel
@app.get("/anuncios")
async def get_anuncios(session: SessionDep):
    try:
        anuncios = session.exec(select(Anuncio)).all()
        anuncios_list = [anuncio.dict() for anuncio in anuncios]
        return {"anuncios": anuncios_list}
    except Exception as e:
        return {"error": "Could not fetch anuncios"}

# Añdir un nuevo endpoint donde se hace un insert de unas cookies 
# a la base de datos utilizando SQLModel
@app.get("/cookie")
async def add_cookie(request: Request, session: SessionDep):
    try:
        cookie_string = request.query_params.get("cookie")

        cookies = cookie_string.split(";")

        for c in cookies:
            nombre, valor = c.strip().split("=", 1)

            nueva_cookie = Cookie(nombre=nombre, valor=valor)
            session.add(nueva_cookie)

        session.commit()

        return {"status": "cookies guardadas"}
    except Exception as e:
        return {"error": "Could not add cookie"}

# Endpoint para listar las cookies guardadas en la base de datos utilizando SQLModel
@app.get("/cookies")
async def get_cookies(session: SessionDep):
    try:
        cookies = session.exec(select(Cookie)).all()
        cookies_list = [cookie.dict() for cookie in cookies]
        return {"cookies": cookies_list}
    except Exception as e:
        return {"error": "Could not fetch cookies"}