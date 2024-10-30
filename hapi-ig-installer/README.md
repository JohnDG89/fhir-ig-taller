# HAPI FHIR Implementation Guide Installer

Este script proporciona una interfaz de línea de comandos para instalar guías de implementación FHIR en un servidor HAPI FHIR utilizando la operación `$install`.

## Características

- Instalación de paquetes NPM de guías de implementación FHIR
- Monitoreo en tiempo real del progreso de instalación
- Barra de progreso visual con indicadores de estado
- Manejo de errores robusto
- Logging detallado de operaciones
- Visualización del tiempo de instalación

## Requisitos

- Python 3.7+
- Bibliotecas Python:
  ```
  requests
  ```

## Uso

### Línea de Comandos

```bash
python ig_installer.py --serverUrl <URL_SERVIDOR> --pkg <RUTA_PAQUETE>
```

Argumentos:

- `--serverUrl`: URL del servidor HAPI FHIR (ej: http://localhost:8080/fhir)
- `--pkg`: Ruta al archivo del paquete NPM (.tgz)

Ejemplo:

```bash
python ig_installer.py --serverUrl http://localhost:8080/fhir --pkg ./npm/clcore_1_9_1.tgz
```

## Logs

El script genera logs detallados en el archivo `ig_install.log`. Los logs incluyen:

- Inicio de la instalación
- Progreso de la operación
- Errores y excepciones
- Resultado final

## Formato de la Operación $install

El script utiliza la operación `ImplementationGuide/$install` de HAPI FHIR, enviando el contenido del paquete NPM en formato Base64:

```json
{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "npmContent",
      "valueBase64Binary": "[BASE64_ENCODED_NPM_PACKAGE_DATA]"
    }
  ]
}
```

## Manejo de Errores

El script maneja varios tipos de errores:

- Archivo no encontrado
- Errores de conexión
- Errores de servidor
- Errores de formato
- Interrupciones del usuario

## Ejemplo de Salida

Instalación Exitosa:

```
Iniciando instalación de clcore_1_9_1.tgz
==================================================
📦 Leyendo paquete...
✓ Paquete leído correctamente

📤 Enviando paquete al servidor...
📋 Verificando respuesta del servidor...
✓ Respuesta del servidor procesada

⏳ Monitoreando instalación...
⏳ Progreso: [████████████████████░░░░░░░░░░] 50% Validando recursos...

==================================================
✅ Instalación completada exitosamente
⏱️  Tiempo total: 00:01:23
==================================================
```

Error de Archivo No Encontrado:

```
❌ Error: No se encontró el archivo: ./no-existe.tgz
```

Error de Conexión:

```
❌ Error: No se pudo conectar al servidor
```

## Ayuda del Script

```bash
python ig_installer.py --help
```

Muestra:

```
usage: ig_installer.py [-h] --serverUrl SERVERURL --pkg PKG

HAPI FHIR Implementation Guide Installer

options:
  -h, --help            show this help message and exit
  --serverUrl SERVERURL
                        URL del servidor HAPI FHIR
                        Ejemplo: http://localhost:8080/fhir
  --pkg PKG             Ruta al archivo del paquete NPM (.tgz)
                        Ejemplo: ./my-implementation-guide.tgz
```
