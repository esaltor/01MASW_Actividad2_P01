# SSRF y SQL Injection Demo – Aplicación Web de Prueba

Esta es una aplicación de demostración de las vulnerabilidades **SSRF (Server-Side Request Forgery)** y **SQL Injection** desarrollada como práctica de seguridad web.  

El proyecto está dividido en dos carpetas:

- `backend` → Código Python + FastAPI
- `frontend` → Código HTML, CSS y JS

---

## 1. Introducción

En cuanto a **SSRF** el objetivo ha sido:

- Implementar una funcionalidad aparentemente legítima en una aplicación web.
- Introducir intencionadamente una vulnerabilidad SSRF en el backend.
- Demostrar su explotación.
- Implementar posteriormente una solución de mitigación.

La aplicación desarrollada simula una herramienta de “vista previa de enlaces”, donde el usuario introduce una URL y el sistema muestra el título de la página indicada.

---

En cuanto a **SQL Injection** el objetivo ha sido:

- Implementar una funcionalidad de autenticación conectada a una base de datos.
- Introducir intencionadamente una vulnerabilidad SQL Injection en el backend.
- Demostrar su explotación mediante manipulación de la consulta.
- Implementar posteriormente una solución segura utilizando consultas parametrizadas.

La aplicación desarrollada incluye un formulario de **login**, donde el usuario introduce su nombre de usuario y contraseña para autenticarse contra una base de datos SQLite.

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
pip install fastapi uvicorn requests beautifulsoup4 sqlalchemy sqlmodel
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
