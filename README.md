
# Documentación de la API

Esta documentación describe los endpoints disponibles en la API desarrollada con Flask y Supabase.

## Autenticación

### 1. Inicio de Sesión

**Endpoint:** `/auth/login`  
**Método:** `POST`  
**Descripción:** Permite a los usuarios iniciar sesión proporcionando sus credenciales.

**Cuerpo de la Solicitud:**
```json
{
    "email": "usuario@example.com",
    "password": "tu_contraseña"
}
```

**Respuesta Exitosa:**
```json
{
    "Mensaje": "Inicio de sesión exitoso",
    "JWT": "token_de_acceso"
}
```

**Errores:**
- **400 Bad Request**: Si faltan credenciales.
    ```json
    {
        "Error": "Faltan credenciales"
    }
    ```
- **500 Internal Server Error**: Si hay un error en la autenticación.
    ```json
    {
        "Error": "Descripción del error"
    }
    ```

---

### 2. Registro de Usuario

**Endpoint:** `/auth/singUp`  
**Método:** `POST`  
**Descripción:** Permite a los usuarios registrarse proporcionando un correo electrónico y una contraseña.

**Cuerpo de la Solicitud:**
```json
{
    "email": "nuevo_usuario@example.com",
    "password": "tu_contraseña"
}
```

**Respuesta Exitosa:**
```json
{
    "Mensaje": "Registro exitoso"
}
```

**Errores:**
- **400 Bad Request**: Si faltan credenciales.
    ```json
    {
        "Error": "Faltan credenciales"
    }
    ```
- **500 Internal Server Error**: Si hay un error en el registro.
    ```json
    {
        "Error": "Descripción del error"
    }
    ```

---

### 3. Cierre de Sesión

**Endpoint:** `/auth/signOut`  
**Método:** `POST`  
**Descripción:** Permite a los usuarios cerrar sesión.

**Respuesta Exitosa:**
```json
{
    "Mensaje": "Cierre de sesión exitoso"
}
```

---

## Manejo de Texto

### 4. Calificación de Texto

**Endpoint:** `/texto`  
**Método:** `POST`  
**Descripción:** Permite enviar un texto para ser calificado y genera un audio a partir de la respuesta.

**Cuerpo de la Solicitud:**
```json
{
    "text": "Texto a calificar"
}
```

**Encabezado Requerido:**
```
Authorization: Bearer token_de_acceso
```

**Respuesta Exitosa:**
```json
{
    "Respuesta_Geminai": "Respuesta de calificación",
    "Audio_URL": "URL_del_audio_generado"
}
```

**Errores:**
- **401 Unauthorized**: Si no se proporciona un token válido.
    ```json
    {
        "Error": "No se proporcionó un token válido"
    }
    ```
- **404 Not Found**: Si no se pudo obtener el texto de la solicitud.
    ```json
    {
        "Respuesta": "No se pudo obtener el texto de la petición"
    }
    ```
- **500 Internal Server Error**: Si hay un error al manejar el texto o generar audio.
    ```json
    {
        "Error": "Descripción del error"
    }
    ```

---

## Despliegue del Servidor Flask

### 1. Clonar el Repositorio

Primero, clona el repositorio de tu proyecto usando `git`:

```bash
git clone https://github.com/Nozguy171/decadencyDevelopment.git
cd decadencyDevelopment

```

### 2. Crear y Activar un Entorno Virtual

Es recomendable usar un entorno virtual para manejar las dependencias del proyecto:

```bash
# Crear un entorno virtual
python3 -m venv venv

# Activar el entorno virtual en Linux/Mac
source venv/bin/activate

# Activar el entorno virtual en Windows
venv\Scripts\activate
```

### 3. Instalar las Dependencias

Instala las dependencias necesarias listadas en el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configurar las Variables de Entorno

Asegúrate de crear un archivo `.env` en el directorio raíz del proyecto con las siguientes variables de entorno:

```
API_KEY=tu_api_key
SUPABASE_URL=tu_supabase_url
SUPABASE_KEY=tu_supabase_key
AWS_AK=tu_access_key_aws
AWS_SAK=tu_secret_access_key_aws
```

### 5. Ejecutar el Servidor Flask

Finalmente, ejecuta el servidor Flask localmente:

```bash
flask run --host=0.0.0.0 --port=5000
```

El servidor debería estar corriendo en [http://localhost:5000](http://localhost:5000).

### 6. Despliegue en Producción (Opcional)

Para despliegue en un entorno de producción, puedes usar servidores como:

- **Heroku**: Una plataforma fácil de usar para despliegue rápido.
- **AWS EC2**: Para mayor control del servidor.
- **Docker**: Para contenedores que pueden ejecutarse en cualquier entorno.

No olvides configurar correctamente el entorno de producción y manejar los certificados SSL para asegurar el tráfico.
