# VPS Framework: Plan de Implementación Unificado (V2)

## 1. Análisis de la Nueva Documentación

He revisado los 12 nuevos documentos (FDD, TDD, CONTRACT y SPECs) para los módulos `PROJECT`, `DEPLOY` y `OPERATE`. 
La arquitectura se mantiene idéntica a la fase HOST: estricta separación de responsabilidades, flujos deterministas, fuerte enfoque en validación cruzada y priorización de Python puro por sobre shell scripts.

### 1.1 Módulo PROJECT (`new-project`)
- **Propósito:** Generar un *scaffold* (esqueleto) estandarizado de proyecto (`app/`, `deploy/`, `project.yaml`, `compose.yaml`, etc).
- **Reglas clave:** 
  - Solo opera en el filesystem (Python-native). No usa `subprocess` ni SSH.
  - Clasifica el target: `CLEAN`, `COMPATIBLE`, `SANEABLE`, `BLOCKED`.
  - Debe preservar datos (no hacer overwrites ciegos) e inyectar un metadata autoritativo (`project.yaml`).

### 1.2 Módulo DEPLOY (`deploy-project`)
- **Propósito:** Convertir el scaffold de PROJECT en un stack ejecutándose en el runtime (Docker Compose).
- **Reglas clave:**
  - Requiere un scaffold válido (chequea `project.yaml`) y un `.env` explícito.
  - Usa el `subprocess_wrapper` (ya construido en HOST) para interactuar con Docker Compose.
  - Clasifica: `READY`, `REDEPLOYABLE`, `BLOCKED`.
  - Requiere *Smoke Tests* para reportar el estatus de éxito. No hay bootstrap de servidor (eso ya lo hizo HOST).

### 1.3 Módulo OPERATE (`audit-project`, `backup-project`)
- **Propósito:** Mantenimiento, backup acotado y observación continua.
- **Reglas clave:**
  - `audit-project`: Clasifica en `HEALTHY`, `DEGRADED`, `BLOCKED`. Solo inspecciona (vía `compose.yaml`), no muta estado. Soporta validación de endpoints (`--endpoint-url`).
  - `backup-project`: Empaqueta determinísticamente el scope del proyecto (usualmente `.tar.gz`), cuidando no expandir el backup a rutas de host no autorizadas. Valida el artefacto post-creación.

---

## 2. Plan de Implementación Completo (Fases Unificadas)

Con `HOST` ya construido como base (`models/`, `utils/subprocess_wrapper.py`, y la CLI Typer raíz), el framework puede escalar de manera incremental. Las siguientes fases seguirán el patrón de Desarrollo Dirigido por Tests (TDD) implementado hasta ahora.

### FASE 9: Project Models & Scaffold Engine
**Dominio:** `PROJECT`
1. **Modelos:** Expandir `enums.py` con las clasificaciones de PROJECT (`TargetClassification`, `ScaffoldAction`).
2. **Scaffold Planner:** Implementar lógica de validación de slug, inspección de rutas (`inspect_target.py`) y decisiones deterministas (`plan.py`).
3. **Renderer & Materializer:** Creador seguro de carpetas y escritor del archivo `project.yaml`.

### FASE 10: CLI `new-project` y Testing
**Dominio:** `PROJECT`
1. Cierre del comando CLI `new-project` en `cli/project_commands.py`.
2. Tests unitarios en Python puro sin dependencias externas del SO (mockeando el file system o usando `tmp_path`).

### FASE 11: Deploy Models & Runtime Wrapping
**Dominio:** `DEPLOY`
1. Expandir `enums.py` con `DeploymentClassification` y `DeployAction`.
2. Crear adaptadores específicos sobre el `subprocess_wrapper` para aislar comandos de Docker Compose (`run_build.py`, `run_up.py`).
3. Integración de validación de configuraciones pre-mutación.

### FASE 12: Smoke Testing y CLI `deploy-project`
**Dominio:** `DEPLOY`
1. Implementar el motor de validación post-run (`smoke.py`), consultando estatus al runtime wrapper.
2. CLI `deploy-project` con reporte unificado, conectando Typer con el Output Generator. Tests unitarios apoyados en mocks.

### FASE 13: Operational Audit Engine
**Dominio:** `OPERATE`
1. Expandir `enums.py` para OPERATE (`AuditClassification`: `HEALTHY`, `DEGRADED`).
2. Implementar lector de `project.yaml` compartido.
3. Creación del `audit-project` pipeline con su CLI correspondiente.

### FASE 14: Bounded Backup Engine
**Dominio:** `OPERATE`
1. Implementar `backup-project` con compresión `.tar.gz` determinista (`archive.py`).
2. Validación de hashes (MD5/SHA256) del artefacto (`checksum.py`).
3. CLI integradora y tests de seguridad (evitar "path traversals").

### FASE 15: Cierre General
1. Ajustes del layout del CLI (colores, consistencia en formato human-readable).
2. Pruebas end-to-end de simulación del ciclo completo:
   `init-vps -> new-project -> deploy-project -> audit-project -> backup-project`.

---

## 3. Estado de la Arquitectura
La base construida en HOST se alinea 100% con este plan. 
* Los **Modelos Base** (`models/`) están listos para recibir los enums nuevos.
* El **Subprocess Wrapper** (`utils/subprocess_wrapper.py`) cumple todas las reglas de DEPLOY (zero-shell, timeout, captura stdout/stderr).
* El motor de output de CLI soportará bien la incorporación de las tablas/secciones para estos nuevos comandos.
