# VPS Framework

**Framework modular en Python para estandarizar el ciclo de vida real de una VPS y de los proyectos que viven sobre ella: preparar el host, crear el proyecto, desplegarlo y operarlo sin automatización cosmética ni supuestos ocultos.**

---

## Qué es

VPS Framework es una plataforma CLI construida en **Python 3.12+** para trabajar con infraestructura y proyectos de forma **determinística, validada y documentada**. Su arquitectura está organizada en cuatro dominios funcionales fijos:

- **HOST** → inspección, clasificación, normalización y hardening del servidor
- **PROJECT** → creación del scaffold base del proyecto
- **DEPLOY** → despliegue controlado del stack
- **OPERATE** → auditoría operativa y backups

La separación en dominios no es decorativa: cada comando pertenece a un único módulo, con responsabilidades y límites explícitos. El orden oficial del framework es **HOST → PROJECT → DEPLOY → OPERATE**. fileciteturn0file6

---

## Por qué nace

La motivación del framework es simple: en la práctica, muchas VPS llegan con estados heterogéneos, cambios manuales previos, configuraciones ambiguas, drift operativo y automatizaciones frágiles. En ese contexto, “que el script no falle” no alcanza. Lo que importa es que el estado final sea **real, verificable y seguro de reutilizar**.

Este framework nace para resolver ese problema con una filosofía fuerte:

- **no asumir entornos limpios**
- **no improvisar comportamiento**
- **no esconder decisiones en scripts shell**
- **no reportar éxito si el estado runtime no fue validado**
- **no mezclar responsabilidades entre módulos**

En otras palabras: no intenta maquillar servidores ni proyectos, sino llevarlos a un estado confiable con reglas claras y verificaciones reales. Esa base está fijada en la arquitectura oficial, en los contratos ejecutables y en el baseline de implementación Python. fileciteturn0file6 fileciteturn0file48

---

## Qué problema resuelve

VPS Framework está pensado para equipos u operadores que quieren dejar atrás este tipo de situaciones:

- VPS “más o menos lista”, pero con estado incierto
- setup manual imposible de reproducir
- scripts Bash que mezclan lógica, decisiones y efectos laterales
- despliegues que “terminan bien” pero dejan servicios caídos
- proyectos sin identidad clara ni metadatos confiables
- backups armados a mano, sin validación del artefacto
- documentación dispersa, ambigua o no accionable por herramientas AI

La propuesta del framework es convertir eso en un flujo trazable:

1. **inspeccionar**
2. **clasificar**
3. **decidir**
4. **ejecutar sólo si es seguro**
5. **validar el resultado real**

---

## Filosofía del proyecto

### 1) Documentación como source of truth

La documentación no está escrita como referencia blanda. Está tratada como material **prescriptivo y ejecutable**: el código debe seguir la documentación, no al revés. Comportamiento no documentado = comportamiento no permitido. fileciteturn0file6

### 2) Python como lenguaje de implementación

Toda la lógica de negocio, clasificación, reconciliación y validación vive en Python. Bash sólo puede aparecer como comando del sistema invocado desde Python, nunca como capa de implementación autónoma. fileciteturn0file6 fileciteturn0file48

### 3) Determinismo

Mismos inputs + mismo estado observado = mismas decisiones, mismas validaciones y mismos códigos de salida. Ese principio cruza HOST, PROJECT, DEPLOY y OPERATE. fileciteturn0file50 fileciteturn0file40 fileciteturn0file38 fileciteturn0file39

### 4) Sin éxito cosmético

Ningún comando debe considerarse exitoso si no puede confirmar el estado final mediante validación real. Esto aplica a host initialization, scaffold de proyecto, despliegue, auditoría y backup. fileciteturn0file50 fileciteturn0file40 fileciteturn0file38 fileciteturn0file39

### 5) Fail closed

Si hay ambigüedad, conflicto o evidencia insuficiente, el framework debe **bloquear**, no adivinar. Esa decisión es intencional: prioriza seguridad y trazabilidad por encima de “seguir igual”. fileciteturn0file37

### 6) Desarrollo asistido por AI, pero gobernado

El proyecto está diseñado para ser trabajado con **Codex (GPT)**, pero bajo protocolos estrictos: prompts con contexto, jerarquía documental, alcance acotado, restricciones y definición de done. La AI no diseña libremente; ejecuta dentro de contratos explícitos. fileciteturn0file42

---

## Arquitectura general

La arquitectura oficial del framework está congelada en cuatro dominios:

### HOST

Responsable de preparar, evaluar, normalizar, validar y asegurar la baseline del servidor. Incluye:

- `audit-vps`
- `init-vps`
- `harden-vps`

Su foco no es desplegar aplicaciones ni crear proyectos, sino transformar una VPS heterogénea en una base confiable para continuar. fileciteturn0file6

### PROJECT

Responsable de crear un scaffold estándar de proyecto mediante:

- `new-project`

Genera estructura, archivos base, convenciones de nombres y metadatos de identidad (`project.yaml`) sin invadir responsabilidades de host ni de despliegue. fileciteturn0file6 fileciteturn0file40

### DEPLOY

Responsable de desplegar el stack del proyecto con:

- `deploy-project`

Valida estructura deployable, runtime, configuración, build, startup, smoke tests y estado final. DEPLOY no repara el host ni crea el scaffold. fileciteturn0file41 fileciteturn0file38

### OPERATE

Responsable de la continuidad operativa con:

- `audit-project`
- `backup-project`

Audita salud del proyecto desplegado y genera backups acotados con validación de artefactos. OPERATE no despliega ni repara HOST. fileciteturn0file45 fileciteturn0file39

---

## Cómo pensar el framework

La mejor forma de entender VPS Framework es esta:

- **HOST** deja el terreno en condiciones
- **PROJECT** construye la estructura base
- **DEPLOY** pone el stack en marcha
- **OPERATE** verifica y protege el resultado

Cada capa depende de la anterior, pero no invade su trabajo. Esa separación reduce deuda técnica, evita solapamientos y permite crecer por slices sin rediseñar todo a cada paso. fileciteturn0file6

---

## Comandos del framework

### HOST

#### `audit-vps`

Audita el estado real de la VPS sin modificar nada. Recolecta evidencia por subprocess controlado desde Python y clasifica el host como:

- `CLEAN`
- `COMPATIBLE`
- `SANEABLE`
- `BLOCKED`

Su trabajo es decidir si el host puede soportar de forma segura la slice actual de inicialización. Revisa, entre otras cosas, OS soportado, arquitectura, viabilidad de SSH, estado del usuario operador, filesystem SSH y señales críticas de seguridad. fileciteturn0file49 fileciteturn0file50

#### `init-vps`

Ejecuta una reconciliación controlada del host, pero **sólo dentro de la slice actual documentada**. Hoy el alcance incluye:

- crear o reutilizar el usuario operador
- asegurar home compatible
- asegurar `.ssh`
- asegurar `authorized_keys`
- asegurar presencia de la clave pública objetivo
- corregir ownership y permisos en paths in-scope
- validar todo luego de mutar

No instala Docker, no cambia firewall, no endurece SSH, no toca sudo/NOPASSWD en esta baseline. Si el host está bloqueado o ambiguo, aborta. fileciteturn0file37 fileciteturn0file50

#### `harden-vps`

Reserva la parte de hardening post-inicialización, especialmente políticas sensibles como endurecimiento SSH. Se mantiene separado para evitar lockouts o mutaciones riesgosas durante la fase de init. fileciteturn0file50

### PROJECT

#### `new-project`

Crea un scaffold determinístico de proyecto a partir de inputs explícitos. Evalúa el target path, lo clasifica y sólo genera o completa lo que sea seguro dentro de la baseline actual. Debe gestionar al menos:

- directorio raíz
- `app/`, `config/`, `deploy/`, `docs/`, `operate/`, `tests/`
- `.env.example`
- `.gitignore`
- `README.md`
- `compose.yaml`
- `project.yaml`

El archivo `project.yaml` es la identidad confiable del proyecto. Sin identidad clara, la operación debe bloquear. fileciteturn0file40

### DEPLOY

#### `deploy-project`

Despliega o re-despliega de forma segura un stack documentado a partir de un proyecto válido. Su flujo obligatorio es:

1. validar inputs
2. inspeccionar proyecto
3. clasificar contexto (`READY`, `REDEPLOYABLE`, `BLOCKED`)
4. validar prerequisitos runtime
5. validar configuración
6. build
7. startup
8. smoke tests
9. validación final

No adivina `.env`, no repara el host, no despliega a ciegas y no reporta éxito sólo porque “docker compose up” terminó. fileciteturn0file41 fileciteturn0file47 fileciteturn0file38

### OPERATE

#### `audit-project`

Audita la salud runtime del proyecto y lo clasifica como:

- `HEALTHY`
- `DEGRADED`
- `BLOCKED`

Valida identidad del proyecto, contexto deploy, disponibilidad del runtime, inspectabilidad del estado y checks de salud base. Puede incluir verificación opcional de endpoint si se pasa explícitamente. No modifica runtime ni intenta “arreglar” lo auditado. fileciteturn0file45 fileciteturn0file46

#### `backup-project`

Crea un backup acotado del proyecto, valida el artefacto y evita expansión oculta del alcance. La baseline actual cubre al menos:

- backup del project root
- artefacto tipo `.tar.gz` recomendado
- checksum sidecar cuando esté implementado
- naming derivado de identidad confiable + timestamp UTC

No incluye paths arbitrarios del host, no restaura y no puede declarar éxito sin validar que el artefacto exista y sea usable. fileciteturn0file45 fileciteturn0file43 fileciteturn0file39

---

## Cómo se usa

### Flujo mental recomendado

Un uso típico del framework sigue esta secuencia:

#### 1. Auditar el host

Primero se inspecciona la VPS real para saber si está limpia, reutilizable, saneable o bloqueada.

```bash
python main.py audit-vps --operator-user <usuario>
```

#### 2. Inicializar sólo si el host es apto

Si el resultado no es `BLOCKED`, puede ejecutarse la slice actual de normalización del host.

```bash
python main.py init-vps --operator-user <usuario> --public-key "<clave_publica>"
```

#### 3. Hardenizar cuando corresponda

La parte de endurecimiento se ejecuta como fase separada, una vez que el acceso seguro ya está validado.

```bash
python main.py harden-vps [opciones]
```

#### 4. Crear un proyecto nuevo

Con el host listo, se genera el scaffold del proyecto.

```bash
python main.py new-project --name <nombre> --path <ruta>
```

#### 5. Desplegar el stack

Con `project.yaml`, `compose.yaml` y env file explícito, se puede desplegar el proyecto.

```bash
python main.py deploy-project --path <ruta_proyecto> --env-file <ruta_env>
```

#### 6. Auditar y respaldar la operación

Una vez desplegado, OPERATE permite verificar salud y crear backups.

```bash
python main.py audit-project --path <ruta_proyecto>
python main.py backup-project --path <ruta_proyecto> --output-dir <ruta_backups>
```

> **Nota:** los nombres exactos de flags y el wiring final de CLI deben seguir la implementación vigente del repositorio. Los comandos anteriores reflejan la baseline documental actual y su intención operativa. fileciteturn0file49 fileciteturn0file47 fileciteturn0file46 fileciteturn0file43

---

## Qué hace distinto a este framework

### No está basado en “scripts mágicos”

Toda la lógica vive en Python, con subprocess wrapper, modelos estructurados, validaciones y tests. Eso vuelve el comportamiento más trazable, más mockeable y más mantenible. fileciteturn0file48

### No mezcla dominios

Cada comando pertenece a un módulo. Si algo corresponde a HOST, no se resuelve desde DEPLOY. Si algo corresponde a OPERATE, no se esconde en PROJECT. Esa separación es una regla arquitectónica, no una preferencia estética. fileciteturn0file6

### Está pensado para crecer por slices

El framework no promete “convergencia total” desde el día uno. Cada módulo define baseline actual, alcance presente, exclusiones y evolución futura documentada. Eso evita scope creep y falsas expectativas. fileciteturn0file50 fileciteturn0file40 fileciteturn0file38 fileciteturn0file39

### Está diseñado para desarrollo AI-assisted serio

La documentación tiene jerarquía, contratos y specs legibles tanto por humanos como por Codex. El objetivo no es “usar IA para codear rápido”, sino usarla como motor controlado dentro de límites bien definidos. fileciteturn0file42

---

## Principios técnicos clave

### Stack técnico base

- **Python 3.12+**
- **Typer** para CLI
- **pytest** para testing
- **ruff** para calidad de código
- `subprocess.run()` o wrapper fino para interacción con sistema
- `dataclasses` y `Enum` para modelado explícito

Ese baseline está formalizado como convención transversal del framework. fileciteturn0file48

### Estructura canónica del repositorio

La estructura base definida para v1 es:

```text
framework/
├── cli/
├── modules/
│   ├── host/
│   ├── project/
│   ├── deploy/
│   └── operate/
├── models/
├── utils/
├── config/
├── tests/
├── main.py
├── pyproject.toml
└── README.md
```

La estructura evita un `core/` genérico y favorece ownership claro por dominio o capa compartida específica. fileciteturn0file48

---

## Estado actual del proyecto

El framework tiene ya definida su arquitectura macro, sus límites por dominio, sus contratos ejecutables y sus baselines funcionales y técnicos por módulo. En particular:

- **HOST** tiene baseline actual centrada en auditoría, primera slice de init y hardening separado. fileciteturn0file37 fileciteturn0file50
- **PROJECT** define el baseline de scaffold determinístico con `new-project`. fileciteturn0file40
- **DEPLOY** define el baseline de despliegue validado con `deploy-project`. fileciteturn0file41 fileciteturn0file44 fileciteturn0file47
- **OPERATE** define el baseline de auditoría operativa y backup. fileciteturn0file45 fileciteturn0file46 fileciteturn0file43

Eso no significa que toda visión futura ya esté implementada. Significa que el proyecto ya tiene una base documental fuerte para crecer de manera ordenada, auditable y sin contradicciones.

---

## Para quién es

VPS Framework está orientado a:

- operadores que administran VPS con criterio reproducible
- consultores que quieren pasar de setup artesanal a baseline gobernada
- equipos que quieren separar claramente host, scaffold, deploy y operación
- proyectos que necesitan documentación utilizable también por herramientas AI
- repositorios que quieren priorizar trazabilidad y contratos por encima de automatización improvisada

No está orientado a “one-click magic” sin contexto. Está orientado a operaciones serias, donde el estado real importa más que una demo bonita.

---

## Qué no intenta ser

Este framework **no** intenta ser:

- un panel visual de hosting
- un PaaS genérico
- un reemplazo de Terraform/Ansible/Kubernetes
- una colección de scripts Bash rápidos
- una caja negra que “hace cosas” sin explicar por qué

Su foco es otro: **orquestación CLI, modular, determinística y validada del ciclo de vida VPS + proyecto**.

---

## En qué se apoya internamente

La gobernanza del framework se basa en una jerarquía documental explícita. A nivel alto, la arquitectura oficial define dominios, ownership y orden de dependencias. Luego cada módulo baja eso a:

- FDD (Functional Design Document)
- TDD (Technical Design Document)
- Contract
- Spec

Y además existe un baseline transversal Python y un protocolo formal para desarrollo con Codex. Esa organización no es burocracia; es lo que permite mantener alineados diseño, implementación y evolución. fileciteturn0file6 fileciteturn0file42 fileciteturn0file48

---

## Visión del framework

La visión de VPS Framework no es simplemente “automatizar tareas”.

La visión es construir una plataforma donde:

- la infraestructura se trate con evidencia real
- el scaffold de proyecto tenga identidad confiable
- el despliegue sea seguro de re-ejecutar
- la operación tenga auditoría y respaldo acotados
- la documentación gobierne al código
- la AI pueda colaborar sin romper diseño ni contratos

Si alguien entra al repositorio y necesita una definición simple, sería esta:

> **VPS Framework es un framework CLI en Python para llevar una VPS y sus proyectos desde un estado heterogéneo a un ciclo operativo gobernado, modular, validado y reproducible.**

---

## Resumen final

VPS Framework existe para convertir infraestructura improvisada y operaciones frágiles en un flujo con:

- dominios claros
- responsabilidades separadas
- inputs explícitos
- decisiones determinísticas
- validación runtime real
- crecimiento por slices documentadas

Si tu forma de trabajar valora más la trazabilidad, la claridad arquitectónica y la validación efectiva que la automatización “mágica”, este framework está hecho exactamente para eso.
