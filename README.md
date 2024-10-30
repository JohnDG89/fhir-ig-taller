# Configuración de Servidor HAPI FHIR e Instalador de IGs

Este proyecto proporciona una configuración completa para levantar un servidor HAPI FHIR usando Docker Compose y herramientas para instalar Guías de Implementación (IGs).

## Estructura del Proyecto

```
.
├── docker-compose.yml          # Configuración de Docker Compose
├── hapi.application.yml        # Configuración de HAPI FHIR
├── hapi-ig-installer/         # Script instalador de IGs
│   ├── ig_installer.py        # Script principal de instalación
│   ├── npm/                   # Directorio para paquetes NPM de IGs
│   │   ├── clcore_1_9_1.tgz  # Ejemplo de paquete IG
│   │   └── ...               # Otros paquetes
│   └── README.md             # Documentación específica del instalador de IGs
└── README.md                  # Este archivo (documentación principal)
```

## Documentación

El proyecto incluye dos archivos README:

1. **README.md (este archivo)**:

   - Documentación principal del proyecto
   - Configuración del servidor HAPI FHIR
   - Instrucciones de Docker Compose

2. **hapi-ig-installer/README.md**:
   - Documentación específica del instalador de IGs
   - Uso detallado del script
   - Ejemplos de instalación de IGs

## Prerrequisitos

- Docker y Docker Compose
- Python 3.7+
- Biblioteca Python `requests`
- 4GB de RAM disponible (mínimo recomendado)
- Puertos disponibles:
  - 8080 (HAPI FHIR)
  - 5432 (PostgreSQL)

## Configuración y Uso

### 1. Levantar el Servidor HAPI FHIR

1. Iniciar los servicios:

```bash
docker compose up -d
```

2. Verificar que los contenedores están corriendo:

```bash
docker compose ps
```

3. Verificar acceso al servidor:

```
http://localhost:8080
```

### 2. Instalación de Guías de Implementación

Ver el README específico en el directorio `hapi-ig-installer` para instrucciones detalladas sobre la instalación de IGs.

## Configuración

### Docker Compose (docker-compose.yml)

Define dos servicios principales:

1. **hapi-fhir-server**:

   - Imagen: hapiproject/hapi:latest
   - Puerto: 8080
   - Configuración personalizada

2. **hapi-fhir-db**:
   - Base de datos PostgreSQL
   - Credenciales:
     - Usuario: admin
     - Contraseña: admin
     - Base de datos: hapi

### HAPI FHIR (hapi.application.yml)

Configuración del servidor con:

- Conexión a PostgreSQL
- Habilitación de carga de IGs

## Gestión del Servidor

### Ver logs:

```bash
# Todos los servicios
docker compose logs

# Solo HAPI FHIR
docker compose logs hapi-fhir-server
```

### Detener servicios:

```bash
docker compose down
```

## Solución de Problemas

### Servidor HAPI FHIR

1. Si los contenedores no inician:

```bash
# Verificar logs
docker compose logs

# Reiniciar servicios
docker compose restart
```

2. Para reiniciar desde cero:

```bash
# Detener y eliminar contenedores
docker compose down

# Eliminar volumen de datos (opcional)
rm -rf ./hapi.postgress.data

# Iniciar nuevamente
docker compose up -d
```

## Persistencia de Datos

Los datos se almacenan en:

- PostgreSQL: `./hapi.postgress.data`
- Logs de instalación de IGs: `./hapi-ig-installer/ig_install.log`

## Notas de Seguridad

- Las credenciales actuales son para desarrollo
- Para producción:
  - Cambiar credenciales de PostgreSQL
  - Configurar seguridad adicional en HAPI FHIR
  - Asegurar el acceso a los endpoints

## Referencias

- [HAPI FHIR Documentación](https://hapifhir.io/)
- [Docker Hub - HAPI FHIR](https://hub.docker.com/r/hapiproject/hapi)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
