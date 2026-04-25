# 🚀 Guía de Ejecución

Para ejecutar el proyecto correctamente, es necesario iniciar 1º el servidor (Backend) y después la interfaz de usuario (Frontend).

## Requisitos Previos
* PostgreSQL instalado y corriendo con la base de datos `rag_db` creada (archivo `script.sql` en el directorio `sql`).
* **Node.js** instalado para el frontend.
* Python 3.x instalado para el backend (en mi caso utilizo **Python 3.14**).

## Paso 1: Configuración de **Base de Datos**
Antes de arrancar, asegúrate de haber ejecutado el script SQL para crear las tablas necesarias:
```
psql -U postgres -d rag_db -f sql/script.sql
```
También puedes abrir el programa de PostgreSQL, crear la BBDD por ti mismo y abrir una query con el script.

## Paso 2: Iniciar el **servidor** (Backend)
### Instalar dependencias si es la primera vez
```
pip install -r requirements.txt
```

### Ejecutar el servidor
```
python run.py
```

## Paso 3: Iniciar la **interfaz** (Frontend)
### Instalar dependencias si es la primera vez
```
npm install
```

### Iniciar la aplicación
```
npm start
```

***
# En este momento, ya tendrás todo listo para trabajar con la app :)