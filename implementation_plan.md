# VPS Framework — Plan de Implementación

---

## PARTE 1: Resumen de lo que entendí de la documentación

### ¿Qué es este proyecto?

Es un **framework modular CLI en Python** diseñado para automatizar la preparación, validación y gestión de servidores VPS (Virtual Private Servers). El framework transforma un VPS heterogéneo (con estado desconocido) en un host predecible, validado y seguro.

### Arquitectura de 4 dominios

El framework se organiza en una cadena de dependencia lineal:

```
HOST → PROJECT → DEPLOY → OPERATE
```

| Módulo | Responsabilidad | Comandos |
|--------|----------------|----------|
| **HOST** | Preparar, auditar, normalizar y asegurar el servidor | `audit-vps`, `init-vps`, `harden-vps` |
| **PROJECT** | Crear scaffold estandarizado de proyecto | `new-project` |
| **DEPLOY** | Desplegar el stack de servicios | `deploy-project` |
| **OPERATE** | Operaciones de continuidad (auditoría, backups) | `audit-project`, `backup-project` |

### Alcance actual: Solo HOST (primer slice)

La documentación deja claro que **solo el módulo HOST está en alcance para implementación ahora**, y específicamente solo el **primer slice de reconciliación** que incluye:

#### `audit-vps` — Diagnóstico read-only
- Inspeccionar estado real del VPS via subprocess
- 9 checks organizados en 5 categorías (OS, USER, SSH, FILESYSTEM, SYSTEM)
- Clasificar el host como: `CLEAN`, `COMPATIBLE`, `SANEABLE` o `BLOCKED`
- Prioridad: `BLOCKED > SANEABLE > COMPATIBLE > CLEAN`
- Salida humana + datos estructurados
- Exit codes determinísticos (0, 1, 2, 3)

#### `init-vps` — Reconciliación controlada (slice 1)
- Gate: abortar si host es `BLOCKED`
- Crear/reusar usuario operador
- Asegurar home del operador
- Asegurar `.ssh/` con permisos correctos
- Asegurar `authorized_keys` con permisos correctos
- Insertar clave pública sin duplicar
- Preservar claves existentes no relacionadas
- Validación post-acción obligatoria
- Idempotente (seguro de re-ejecutar)

#### `harden-vps` — Hardening post-inicialización
- Deshabilitar password auth
- Restringir root login
- SSH policy estricta
- Solo se ejecuta después de init exitoso

### Reglas de ingeniería no negociables

1. **Python only** — toda la lógica en Python 3.12+
2. **Bash solo como sistema ejecutado** — via `subprocess.run()`, nunca como lógica propia
3. **CLI via Typer** — capa delgada, sin lógica de negocio
4. **Determinismo** — mismos inputs + mismo estado = mismos resultados
5. **Runtime validation** — nada es exitoso sin validación en ejecución
6. **Idempotencia** — operaciones seguras de re-ejecutar
7. **Abort on ambiguity** — ante duda, abortar (no adivinar)
8. **Documentación prescriptiva** — el código sigue a la documentación, no al revés
9. **Sin hardcoding** — identidad de operador y claves son inputs explícitos

### Tecnologías y herramientas

- **Python 3.12+**
- **Typer** para CLI
- **dataclasses** y **Enum** para modelos
- **subprocess.run()** para interacción con el sistema
- **pytest** para tests
- **ruff** para linting/formatting
- **pyproject.toml** para dependencias

---

## PARTE 2: Plan de Implementación Detallado

### Estructura objetivo del repositorio

```
framework/
├── cli/
│   ├── __init__.py
│   └── host_commands.py          # Typer commands para audit/init/harden
├── modules/
│   └── host/
│       ├── __init__.py
│       ├── audit/
│       │   ├── __init__.py
│       │   ├── checks_os.py      # CHECK_OS_01, CHECK_OS_02
│       │   ├── checks_user.py    # CHECK_USER_01, CHECK_USER_02
│       │   ├── checks_ssh.py     # CHECK_SSH_01, CHECK_SSH_02
│       │   ├── checks_fs.py      # CHECK_FS_01, CHECK_FS_02
│       │   ├── checks_system.py  # CHECK_SYS_01
│       │   ├── classifier.py     # Reduce results → classification
│       │   └── runner.py         # Orquesta checks + output
│       ├── init/
│       │   ├── __init__.py
│       │   ├── reconcile_user.py
│       │   ├── reconcile_filesystem.py
│       │   ├── validate.py
│       │   └── runner.py
│       └── harden/
│           ├── __init__.py
│           └── runner.py         # Placeholder con abort seguro
├── models/
│   ├── __init__.py
│   ├── check_result.py           # CheckResult dataclass
│   ├── enums.py                  # CheckStatus, HostClassification, ClassificationImpact
│   └── command_result.py         # CommandOutcome para subprocess
├── utils/
│   ├── __init__.py
│   ├── subprocess_wrapper.py     # Wrapper centralizado
│   └── output.py                 # Formateo de output humano
├── config/
│   ├── __init__.py
│   └── host_config.py            # Thresholds, supported versions, etc.
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_subprocess_wrapper.py
│   ├── test_audit_checks.py
│   ├── test_classifier.py
│   ├── test_audit_runner.py
│   ├── test_reconcile_user.py
│   ├── test_reconcile_filesystem.py
│   ├── test_validate.py
│   └── test_init_runner.py
├── main.py                       # Root CLI app
├── pyproject.toml
└── README.md
```

---

### FASE 1: Scaffolding del proyecto
**Objetivo**: Crear la estructura base del repositorio

**Tareas**:
1. Crear `pyproject.toml` con dependencias: `typer`, `pytest`, `ruff`
2. Crear toda la estructura de directorios con `__init__.py`
3. Crear `main.py` como punto de entrada Typer root
4. Verificar que `python main.py --help` funciona

**Entregables**: Proyecto ejecutable vacío con CLI Typer registrado

---

### FASE 2: Modelos compartidos (models/)
**Objetivo**: Definir las estructuras de datos base

**Tareas**:
1. `models/enums.py`:
   - `CheckStatus` enum: `OK`, `WARN`, `FAIL`
   - `HostClassification` enum: `CLEAN`, `COMPATIBLE`, `SANEABLE`, `BLOCKED`
   - `ClassificationImpact` enum: `NONE`, `SANEABLE`, `BLOCKED`
2. `models/check_result.py`:
   - `CheckResult` dataclass con: `check_id`, `title`, `category`, `description`, `evidence_command`, `expected_behavior`, `status`, `evidence`, `message`, `classification_impact`
3. `models/command_result.py`:
   - `CommandResult` dataclass para subprocess: `stdout`, `stderr`, `returncode`, `timed_out`

**Entregables**: Modelos importables, sin dependencias externas

---

### FASE 3: Subprocess Wrapper (utils/)
**Objetivo**: Centralizar la ejecución de comandos del sistema

**Tareas**:
1. `utils/subprocess_wrapper.py`:
   - Función `run_command(cmd_list, timeout=30) → CommandResult`
   - Lista de argumentos explícita (no `shell=True`)
   - Captura stdout, stderr, returncode
   - Manejo de timeout
   - Manejo de excepciones (FileNotFoundError, etc.)
2. Tests unitarios para el wrapper

**Entregables**: Wrapper testeable y mockeable

---

### FASE 4: Configuración HOST (config/)
**Objetivo**: Externalizar valores configurables documentados

**Tareas**:
1. `config/host_config.py`:
   - `SUPPORTED_OS_IDS`: `["ubuntu"]`
   - `SUPPORTED_UBUNTU_VERSIONS`: `["22.04", "24.04"]`
   - `SUPPORTED_ARCHITECTURES`: `["x86_64", "aarch64"]`
   - `MIN_FREE_SPACE_MB`: threshold documentado (ej: 500)
   - `LOW_FREE_SPACE_MB`: threshold para WARN (ej: 1000)
   - Permisos esperados para `.ssh` (700), `authorized_keys` (600), home (755)

**Entregables**: Configuración explícita y documentada

---

### FASE 5: Audit Checks (modules/host/audit/)
**Objetivo**: Implementar los 9 checks de auditoría

**Tareas** (un archivo por familia de checks):

1. **`checks_os.py`**:
   - `run_check_os_supported(operator_user)` → parsea `/etc/os-release`, valida ID y VERSION_ID
   - `run_check_os_architecture()` → ejecuta `uname -m`, valida contra lista soportada

2. **`checks_user.py`**:
   - `run_check_user_exists(operator_user)` → ejecuta `id <user>`
   - `run_check_user_home_mapping(operator_user)` → ejecuta `getent passwd <user>`, parsea home y shell

3. **`checks_ssh.py`**:
   - `run_check_ssh_syntax()` → ejecuta `sshd -t`, valida exit code
   - `run_check_ssh_effective_config()` → ejecuta `sshd -T`, parsea `pubkeyauthentication`, `passwordauthentication`, `permitrootlogin`, `kbdinteractiveauthentication`

4. **`checks_fs.py`**:
   - `run_check_operator_home_state(operator_user)` → ejecuta `stat` sobre home
   - `run_check_operator_ssh_paths(operator_user)` → ejecuta `stat` sobre `.ssh` y `authorized_keys`

5. **`checks_system.py`**:
   - `run_check_root_free_space()` → ejecuta `df -Pk /`, parsea espacio disponible

6. **`classifier.py`**:
   - `reduce_classification(results: list[CheckResult]) → HostClassification`
   - Lógica de prioridad: BLOCKED > SANEABLE > COMPATIBLE > CLEAN

7. **`runner.py`** (audit runner):
   - `run_audit(operator_user) → AuditReport`
   - Ejecuta todos los checks en orden
   - Agrega resultados
   - Reduce clasificación
   - Retorna reporte estructurado

**Cada función**:
- Recibe dependencias explícitas (operator_user)
- Retorna `CheckResult`
- Sin side effects ni prints directos
- Totalmente testeable via mock del subprocess wrapper

**Entregables**: 9 checks + clasificador + runner, todos con tests

---

### FASE 6: Init Reconciliation — Slice 1 (modules/host/init/)
**Objetivo**: Implementar la reconciliación controlada del primer slice

**Tareas**:

1. **`reconcile_user.py`**:
   - `reconcile_operator_user(operator_user) → ReconcileResult`
   - Chequear si usuario existe (`id`)
   - Si existe y es compatible → reusar
   - Si no existe → crear con `useradd`
   - Si estado ambiguo → abort (retornar BLOCKED)

2. **`reconcile_filesystem.py`**:
   - `reconcile_operator_home(operator_user, expected_home) → ReconcileResult`
   - `reconcile_ssh_directory(operator_user, expected_home) → ReconcileResult`
   - `reconcile_authorized_keys(operator_user, expected_home, public_key) → ReconcileResult`
   - Cada función:
     - Inspeccionar estado actual
     - Crear si no existe
     - Ajustar permisos/ownership si necesario
     - Preservar contenido existente
     - No duplicar clave pública
     - Abort ante estado ambiguo

3. **`validate.py`**:
   - `validate_init_slice(operator_user, expected_home, public_key) → ValidationReport`
   - Validar post-acción:
     - Usuario existe
     - Home existe con ownership correcto
     - `.ssh` existe con permisos 700
     - `authorized_keys` existe con permisos 600
     - Clave pública presente en el archivo
   - Si cualquier validación falla → operación FAILED

4. **`runner.py`** (init runner):
   - `run_init(operator_user, public_key_path) → InitResult`
   - Flujo:
     1. Validar inputs explícitos
     2. Ejecutar audit gate (clasificación)
     3. Si BLOCKED → abort con exit code 2
     4. Ejecutar reconciliación de usuario
     5. Ejecutar reconciliación de filesystem
     6. Ejecutar validación post-acción
     7. Emitir resultado determinístico

**Entregables**: Reconciliación completa del slice 1 con validación, totalmente testeable

---

### FASE 7: CLI Layer (cli/ + main.py)
**Objetivo**: Exponer los comandos HOST via Typer

**Tareas**:

1. **`cli/host_commands.py`**:
   - `audit_vps(operator_user: str)` → invoca audit runner, renderiza output, exit code
   - `init_vps(operator_user: str, public_key: str)` → invoca init runner, renderiza output, exit code
   - `harden_vps()` → placeholder con mensaje "Not yet implemented in current slice"

2. **`main.py`**:
   - App Typer root
   - Registrar subcomandos host: `audit-vps`, `init-vps`, `harden-vps`

3. **`utils/output.py`**:
   - Funciones para renderizar output human-readable:
     - Output agrupado por categoría (OS, USER, SSH, FILESYSTEM, SYSTEM)
     - Cada línea: `[STATUS] CHECK_ID — message`
     - Clasificación final clara
     - Contadores de resumen (total, ok, warn, fail)

4. **Exit codes**:
   - `0` → todo OK, sin warnings
   - `1` → warnings presentes, sin BLOCKED
   - `2` → failures/BLOCKED detectados
   - `3` → error de runtime del propio audit

**Entregables**: CLI funcional con los 3 comandos registrados

---

### FASE 8: Tests e Integración
**Objetivo**: Cobertura de tests según documentación

**Tareas**:

1. **Tests de modelos**: Enum values, dataclass creation
2. **Tests de subprocess wrapper**: Mock de subprocess.run, timeout, error handling
3. **Tests de audit checks**: Mock de evidencias del sistema, validar parsing y status correcto
4. **Tests de clasificador**: Combinaciones de resultados → clasificación esperada
5. **Tests de audit runner**: Flujo completo con mocks
6. **Tests de reconciliación**: 
   - Usuario existe → reusar
   - Usuario no existe → crear
   - Estado ambiguo → abort
7. **Tests de filesystem**:
   - Path missing → crear
   - Permisos incorrectos → corregir
   - Key ya presente → no duplicar
   - Estado conflictivo → abort
8. **Tests de validación**: Post-acción pass/fail
9. **Tests de init runner**: Flujo completo gate → reconcile → validate
10. **Tests de seguridad**:
    - BLOCKED host → abort
    - Ambiguity → abort
    - Idempotencia en re-run
    - Preservación de keys existentes

**Entregables**: Suite de tests que pasa en Windows (mocked) sin requerir Linux

---

## Orden de Ejecución Recomendado

| Paso | Fase | Depende de |
|------|------|------------|
| 1 | FASE 1: Scaffolding | — |
| 2 | FASE 2: Modelos | Fase 1 |
| 3 | FASE 3: Subprocess Wrapper | Fase 1 |
| 4 | FASE 4: Configuración | Fase 1 |
| 5 | FASE 5: Audit Checks | Fases 2, 3, 4 |
| 6 | FASE 6: Init Reconciliation | Fases 2, 3, 4, 5 |
| 7 | FASE 7: CLI Layer | Fases 5, 6 |
| 8 | FASE 8: Tests | Todas las anteriores |

> [!NOTE]
> Las fases 2, 3 y 4 son independientes entre sí y pueden ejecutarse en paralelo.
> Los tests de cada fase deberían escribirse junto con la implementación (no al final), pero los agrupo en la Fase 8 por claridad del plan.

> [!IMPORTANT]
> **Ambiente de desarrollo**: Todo se desarrolla en Windows. Los tests deben mockear subprocess para no requerir Linux real. La ejecución real es contra un VPS Ubuntu.

> [!WARNING]
> **harden-vps** está documentado pero es intencionalmente un placeholder en el slice actual. No se implementa su lógica, solo el registro CLI con mensaje apropiado.

---

## Restricciones que debo respetar

1. **No improvisar** — solo implementar lo documentado
2. **No hardcodear** operator user ni public key
3. **No mezclar** responsabilidades entre módulos
4. **No shell=True** excepto justificación fuerte
5. **No prints** dentro de lógica de negocio
6. **No asumir** máquina limpia
7. **No reportar éxito** sin validación runtime
8. **No expandir scope** más allá del slice documentado
