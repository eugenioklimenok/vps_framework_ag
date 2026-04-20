# Guía de Prueba en VPS Real (Linux)

Esta guía detalla el paso a paso para probar el **VPS Framework** en un entorno de servidor real (ej. Ubuntu Server). Abarca la configuración inicial y el uso secuencial de los 4 dominios del framework (`HOST`, `PROJECT`, `DEPLOY`, `OPERATE`).

> [!IMPORTANT]
> **Requisitos Previos en el VPS:**
> - Sistema operativo Linux (Ubuntu preferentemente).
> - Python 3.12+ instalado.
> - Git instalado para clonar el repositorio.
> - Docker y Docker Compose (requerido por los comandos de despliegue).

---

## 1. Preparación del Entorno

Primero, conéctate a tu VPS como usuario `root` o un usuario con permisos de sudo, y descarga el framework.

```bash
# 1. Conectarse al VPS
ssh root@<IP_DEL_VPS>

# 2. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO> /opt/vps_framework_ag
cd /opt/vps_framework_ag

# 3. Crear y activar un entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# 4. Instalar el framework y sus dependencias
pip install -e ".[dev]"
```

Comprueba que el CLI responde correctamente:
```bash
python main.py --help
```

---

## 2. Dominio HOST: Preparación del Servidor

Este dominio se encarga de auditar e inicializar el entorno base del servidor, asegurando que un "usuario operador" específico exista y esté correctamente configurado.

### Paso 2.1: Auditoría Inicial
Realiza un diagnóstico de solo lectura para comprobar el estado actual del host respecto al usuario operador (por ejemplo, `devops`).

```bash
python main.py host audit-vps --operator-user devops
```

### Paso 2.2: Inicialización del Host
Si no tienes una llave pública SSH a mano, crea una temporal para la prueba (en un entorno real, usa la tuya propia):
```bash
ssh-keygen -t ed25519 -f /tmp/test_key -N ""
```

Ejecuta la reconciliación para crear el usuario y configurarlo:
```bash
python main.py host init-vps \
  --operator-user devops \
  --public-key /tmp/test_key.pub
```
> [!NOTE]
> Al finalizar este paso, el framework habrá creado el usuario `devops`, configurado `sudo` sin contraseña (NOPASSWD) y establecido tu llave SSH autorizada de forma inmutable.

---

## 3. Dominio PROJECT: Creación del Scaffold

Una vez que el servidor está listo, generamos la estructura determinística del nuevo proyecto.

```bash
# Cambia al usuario operador que acabas de crear (recomendado por permisos)
su - devops
cd /opt/vps_framework_ag
source venv/bin/activate

# Generar el nuevo proyecto
python main.py project new-project \
  --name "mi-app-demo" \
  --path "/home/devops/mi-app-demo"
```

Esto validará la ruta de destino e instalará la estructura de directorios determinística, incluyendo templates de `.env`, y bases de scaffolding para el stack.

---

## 4. Dominio DEPLOY: Despliegue del Stack

Convierte la estructura del proyecto recién generado en un stack dockerizado en ejecución.

### Paso 4.1: Configurar Variables de Entorno
Copia el archivo de ejemplo generado por el proyecto para crear un `.env` real:
```bash
cp /home/devops/mi-app-demo/.env.example /home/devops/mi-app-demo/.env
```
*(Puedes editar `/home/devops/mi-app-demo/.env` si es necesario configurar contraseñas o puertos personalizados antes de desplegar).*

### Paso 4.2: Ejecutar el Despliegue
Levanta el proyecto validando la estructura:
```bash
python main.py deploy deploy-project \
  --path "/home/devops/mi-app-demo" \
  --env-file "/home/devops/mi-app-demo/.env"
```
> [!TIP]
> Este comando valida la estructura del proyecto, confirma que el `.env` esté bien formado, asegura que Docker esté en ejecución, levanta el compose y realiza *smoke tests* para verificar la salud inicial del stack.

---

## 5. Dominio OPERATE: Mantenimiento y Respaldos

El último dominio permite mantener el proyecto a lo largo del tiempo (auditoría en caliente y backups inmutables).

### Paso 5.1: Auditoría de Salud del Proyecto
Comprueba que los contenedores del proyecto estén corriendo correctamente en tiempo real.
```bash
python main.py operate audit-project \
  --path "/home/devops/mi-app-demo" \
  --env-file "/home/devops/mi-app-demo/.env"
```
*(Puedes añadir `--endpoint-url http://localhost:8080` opcionalmente si tu proyecto expone una URL HTTP y quieres que el framework verifique una respuesta `200 OK`).*

### Paso 5.2: Creación de Respaldo
Genera un backup determinístico y aislado de toda la configuración y estado (tarball comprimido).
```bash
python main.py operate backup-project \
  --path "/home/devops/mi-app-demo" \
  --include-env
```
> [!WARNING]
> La flag `--include-env` es opcional e incluye el archivo con secretos en el `.tar.gz`. Se recomienda usarlo solo en entornos de prueba. En un escenario de producción real, debes encargarte de encriptar el archivo de salida inmediatamente o enviarlo a un Cold Storage seguro.

El CLI indicará la ruta exacta del artefacto `.tar.gz` (usualmente en `/tmp/...` u otro directorio provisto por el OS).

---

## Resumen de la Ejecución de Extremo a Extremo

```bash
# 1. Configurar Host
python main.py host init-vps -u oper -k /tmp/key.pub

# 2. Crear Proyecto
python main.py project new-project --name testapp --path /var/www/testapp

# 3. Preparar .env
cp /var/www/testapp/.env.example /var/www/testapp/.env

# 4. Desplegar
python main.py deploy deploy-project --path /var/www/testapp --env-file /var/www/testapp/.env

# 5. Auditar y Respaldar
python main.py operate audit-project --path /var/www/testapp --env-file /var/www/testapp/.env
python main.py operate backup-project --path /var/www/testapp
```
