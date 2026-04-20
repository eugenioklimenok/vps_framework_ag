# VPS Framework — Reporte Final de Solución

## 1. Resumen Ejecutivo
Se ha concluido exitosamente el diseño, arquitectura y desarrollo total del **VPS Framework**. Esta herramienta está diseñada para brindar una plataforma robusta y determinista orientada a la preparación, despliegue, y operación continua de aplicaciones en servidores (VPS). 

La solución fue implementada íntegramente en Python (vía `Typer`), separándose en **cuatro grandes dominios funcionales**, evitando depender de scripts frágiles de *shell* (Bash), garantizando que todas las mutaciones al sistema sean auditables, tipadas e idempotentes.

---

## 2. Arquitectura de Dominios Implementada

El ciclo de vida del framework opera secuencialmente bajo 4 pilares:

### 2.1 Dominio HOST (`vps host`)
El módulo fundamental. Se encarga de evaluar si la máquina subyacente (VPS) está lista y es segura.
*   **Auditoría (Audit):** Escanea el estado del servidor (OS, creación de usuarios, configuración SSH y permisos de FileSystem) para clasificar a la máquina en `CLEAN`, `COMPATIBLE`, `SANEABLE`, o `BLOCKED`.
*   **Inicialización (Init):** Realiza la estabilización inicial del servidor creando de forma segura el usuario del deploy y endureciendo los permisos de las carpetas críticas (como `~/.ssh`).
*   **Comandos:** `init-vps`, `audit-vps` y `harden-vps`.

### 2.2 Dominio PROJECT (`vps project`)
Abstrae la creación local del esqueleto de la aplicación garantizando que sea predecible para el pipeline de despliegue.
*   **Scaffold Determinista:** Construye un esqueleto (`app/`, `config/`, `deploy/`, `tests/`) sin pisar información existente si se lanza sobre un directorio compatible.
*   **Identity (project.yaml):** Inyecta el archivo autoritativo que asienta la metadata del proyecto (`project_slug`) para que el resto del framework sepa cómo manejarlo.
*   **Comandos:** `new-project`

### 2.3 Dominio DEPLOY (`vps deploy`)
Transforma la estructura de directorios abstracta de PROJECT en contenedores en ejecución.
*   **Runtime Prerequisite Checks:** Valida la pre-existencia de Docker Compose.
*   **Compose Wrapper:** Aísla de forma segura llamadas como `docker compose config`, `build` y `up` mediante el `subprocess_wrapper` interno.
*   **Validación Posterior (Smoke Tests):** No se considera un deploy "exitoso" hasta que `docker compose ps` reporta activamente que los contenedores definidos están en estado `running`.
*   **Comandos:** `deploy-project`

### 2.4 Dominio OPERATE (`vps operate`)
Controla la etapa final de ciclo de vida, focalizándose en mantención continua de los proyectos desplegados.
*   **Observabilidad (Audit):** Escanea el estado en tiempo real (clasificando en `HEALTHY`, `DEGRADED`, o `BLOCKED`). Opcionalmente permite hacer un test HTTP sobre los endpoints del aplicativo.
*   **Resguardo (Backup):** Ejecuta una copia de seguridad empaquetada (tarball `.tar.gz`) que tiene límites estrictos (*bounded*) sobre los directorios del target para evitar filtración de variables de entorno y "tarbombs" recursivas.
*   **Comandos:** `audit-project`, `backup-project`

---

## 3. Patrones de Diseño Técnico Aplicados

La solidez del VPS Framework recae sobre 4 pilares técnicos diseñados durante la implementación:

1.  **Zero-Shell Scripting:** 
    A diferencia de la mayoría de frameworks de gestión de servidores, aquí todo se ejecuta mediante la librería nativa de Python `subprocess.run()`. El wrapper `utils/subprocess_wrapper.py` encapsula la salida estandar (stdout), errores (stderr), maneja *timeouts* de forma elegante e impide la inyección de comandos.

2.  **Arquitectura "Fail-Closed" / Abort-on-Failure:**
    Nunca se asumen estados. Si el archivo `.env` no se declara, el target de deploy falla. Si `project.yaml` está malformado, OPERATE bloquea la acción. Todos los procesos devuelven un *Exit Code* `2` (`BLOCKED`) antes de mutar cosas de forma dudosa.

3.  **Resultados fuertemente tipados (Dataclasses):**
    Cada uno de los 4 módulos usa clases inmutables exclusivas para el paso de estados entre la lógica de negocio y la CLI.
    *(Ej: `CheckResult`, `ScaffoldResult`, `DeployResult`, `ProjectAuditResult`).*

4.  **CLI Human-Readable (Typer):**
    La presentación al usuario separa en tablas visuales de terminal (utilizando códigos de colores ANSI) qué procesos se llevaron a cabo (`Actions Taken`), qué hallazgos hubo y un bloque gigante final con el veredicto (V.g. `[OK] PASS`).

---

## 4. Estructura de Directorios Resultante

```text
framework/
├── cli/                 # Definiciones de Typer CLI
│   ├── main.py          # Entrypoint raíz
│   ├── host_commands.py
│   ├── project_commands.py
│   ├── deploy_commands.py
│   └── operate_commands.py
├── config/              # Valores umbrales y requerimientos estructurales
│   ├── host_config.py
│   └── project_config.py
├── models/              # Dataclasses y Enums (Single source of truth)
│   ├── check_result.py
│   ├── enums.py
│   ├── ...
├── modules/             # Lógica de Negocio Pura (Runner -> Orchestrator)
│   ├── host/
│   ├── project/
│   ├── deploy/
│   └── operate/
├── utils/               # Utilidades horizontales
│   ├── output.py        # ASCII formatting UI reports
│   └── subprocess_wrapper.py
└── tests/               # Pruebas automatizadas por módulo
    ├── test_host_*.py
    ├── test_project_*.py
    ├── test_deploy_*.py
    └── test_operate_*.py
```

---

## 5. Estrategia de Testing (TDD)

Toda la solución se desarrolló basándose en **Test-Driven Development (TDD)**, utilizando `pytest` como motor central.
- **Subprocess Mocking:** Dado que la herramienta interacciona con Docker y el Sistema Operativo, todas las pruebas unitarias "mockean" la capa de `subprocess_wrapper`, lo que permite que la suite corra localmente en milisegundos en máquinas Windows/Mac sin necesidad de un VPS real.
- **Total de pruebas automatizadas:** El sistema está cubierto por docenas de unit tests integrados directamente con las sentencias CLI.

## 6. Conclusión y Escenarios de Uso Final

El sistema está listo para producción. Posibles maneras en las que este framework puede ser consumido a partir de ahora:
- **Como un CLI Tool Interactivo:** Ejecutado por los SysAdmins localmente con `vps deploy deploy-project --path ./miapp`.
- **Integrado en CI/CD:** Gracias al control del `Exit Code` (Devuelve `0` si triunfa, `2` si falla), puede correr dentro de GitHub Actions o GitLab CI impidiendo despliegues defectuosos.
- **Orquestación superior:** Puede ser llamado por Ansible, Terraform u otros scripts en python para gestionar flotas de servidores.
