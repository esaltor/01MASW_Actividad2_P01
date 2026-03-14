# Stored XSS Demo – Aplicación Web de Prueba

Esta es una aplicación de demostración de la vulnerabilidad **Stored XSS (Cross-Site Scripting persistente)** desarrollada como práctica de seguridad web. 

El proyecto está dividido en dos carpetas:

- `backend` → Código Python + FastAPI
- `frontend` → Código HTML, CSS y JS

---

## 1. Introducción

En cuanto a **XSS** el objetivo ha sido:

Implementar un sistema de anuncios donde los usuarios puedan publicar título, descripción, precio y nombre del vendedor.

Introducir intencionadamente una vulnerabilidad Stored XSS en el campo de descripción del anuncio.

Demostrar su explotación mediante la ejecución de código JavaScript en el navegador de otros usuarios.

Implementar posteriormente una solución de mitigación mediante sanitización y escape de caracteres en el backend y frontend.

La aplicación permite publicar anuncios a través de un formulario HTML y almacenarlos en SQLite mediante endpoints de FastAPI (POST /anuncio y GET /anuncios). La vulnerabilidad se produce porque el contenido de los anuncios se muestra directamente en el frontend con innerHTML sin escaparse.

---

## 2. Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- Python 3.10+ (o superior)
- pip
- Navegador moderno (Chrome, Firefox, Edge)
- Opcional: `virtualenv` para crear entorno virtual

Dependencias Python:

```bash
pip install fastapi uvicorn requests beautifulsoup4
```

## 3. Instalación y puesta en marcha del backend

Abrir terminal en la carpeta backend:

```bash
cd backend
```

Crear un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
```

Activar el entorno virtual:

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Si no tienes requirements.txt:

```bash
pip install fastapi[standard] uvicorn requests beautifulsoup4 sqlalchemy sqlmodel
```

Ejecutar el backend:

```bash
uvicorn main:app --reload
```

Por defecto, FastAPI correrá en:

```cpp
http://127.0.0.1:8000
```

## 4. Instalación y puesta en marcha del frontend

Asegúrate de tener Node.js y npm instalados.

Abre terminal en la carpeta frontend:

```bash
cd frontend
```

Instala Parcel (si no lo tienes globalmente):

```bash
npm install -D parcel
```

O si lo quieres global:

```bash
npm install -g parcel
```

Arranca el frontend usando Parcel:

```bash
npx parcel src/index.html
```

Esto creará un servidor de desarrollo.

Por defecto, Parcel servirá la aplicación en:

```cpp
http://localhost:1234
```

Abre el navegador en esa URL para interactuar con la aplicación.
