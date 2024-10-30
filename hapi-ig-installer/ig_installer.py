import requests
import json
import time
import logging
import argparse
import base64
from typing import Optional, Dict, Any, Union, Tuple
from pathlib import Path
import sys
from datetime import datetime

class HAPIImplementationGuideInstaller:
    def __init__(self, serverUrl: str):
        self.serverUrl = serverUrl.rstrip('/')
        self.setup_logging()
        self.start_time = None

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('ig_install.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def install_implementation_guide(self, pkg: str) -> bool:
        """
        Instala una guía de implementación usando la operación $install.
        """
        self.start_time = datetime.now()
        try:
            # Mostrar inicio de la operación
            pkg_name = Path(pkg).name
            self.logger.info(f"Iniciando instalación de {pkg_name}")
            print(f"\nIniciando instalación de {pkg_name}")
            print("=" * 50)

            # Leer y validar el archivo
            print("📦 Leyendo paquete...")
            with open(pkg, 'rb') as file:
                package_content = file.read()
                base64_content = base64.b64encode(package_content).decode('utf-8')
            print("✓ Paquete leído correctamente")

            # Preparar los parámetros
            parameters = {
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "npmContent",
                        "valueBase64Binary": base64_content
                    }
                ]
            }

            # Ejecutar la operación $install
            install_url = f"{self.serverUrl}/ImplementationGuide/$install"
            print("\n📤 Enviando paquete al servidor...")
            
            response = requests.post(
                install_url,
                json=parameters,
                headers={'Content-Type': 'application/fhir+json'}
            )

            # Procesar la respuesta inicial
            print("📋 Verificando respuesta del servidor...")
            success, task_id = self._process_response(response)
            
            if not success:
                self._show_completion_status(False)
                return False

            # Si hay task_id, monitorear la instalación
            if task_id:
                print("\n⏳ Monitoreando instalación...")
                return self._monitor_installation(task_id)
            else:
                # Si no hay task_id pero la operación fue exitosa
                print("\n✓ Instalación procesada por el servidor")
                self._show_completion_status(True)
                return True

        except FileNotFoundError:
            self.logger.error(f"No se encontró el archivo: {pkg}")
            print(f"\n❌ Error: No se encontró el archivo: {pkg}")
            return False
        except Exception as e:
            self.logger.error(f"Error durante la instalación: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            return False

    def _process_response(self, response: requests.Response) -> Tuple[bool, Optional[str]]:
        """
        Procesa la respuesta del servidor y extrae el task ID si está disponible.
        """
        try:
            if response.status_code not in [200, 201]:
                print(f"\n❌ Error del servidor: {response.status_code}")
                self.logger.error(f"Error del servidor: {response.status_code}")
                self.logger.error(response.text)
                return False, None

            # Intentar parsear la respuesta
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                print("\n⚠️  Respuesta no JSON del servidor")
                self.logger.warning("La respuesta no es JSON válido")
                return True, None

            # Procesar diferentes tipos de respuesta
            if response_data.get("resourceType") == "Task":
                print("✓ Tarea de instalación creada")
                return True, response_data.get("id")

            if response_data.get("resourceType") == "Parameters":
                for param in response_data.get("parameter", []):
                    if param.get("name") == "taskId":
                        print("✓ ID de tarea recibido")
                        return True, param.get("valueString")

            if response_data.get("resourceType") == "OperationOutcome":
                # Verificar si hay errores
                issues = response_data.get("issue", [])
                for issue in issues:
                    severity = issue.get("severity", "")
                    details = issue.get("diagnostics", "Sin detalles")
                    print(f"{'❌' if severity == 'error' else '⚠️'} {severity.upper()}: {details}")
                    
                has_errors = any(issue.get("severity") == "error" for issue in issues)
                if has_errors:
                    return False, None

            print("✓ Respuesta del servidor procesada")
            return True, None

        except Exception as e:
            self.logger.error(f"Error procesando respuesta: {str(e)}")
            print(f"\n❌ Error procesando respuesta: {str(e)}")
            return False, None

    def _monitor_installation(self, task_id: str, poll_interval: int = 2) -> bool:
        """
        Monitorea el progreso de la instalación.
        """
        previous_progress = -1
        try:
            while True:
                status = self._get_task_status(task_id)
                if not status:
                    self._show_completion_status(False)
                    return False

                current_progress = self._display_progress(status, previous_progress)
                if current_progress != previous_progress:
                    previous_progress = current_progress

                if status.get('status') in ['completed', 'failed']:
                    success = status.get('status') == 'completed'
                    self._show_completion_status(success)
                    return success

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n\n⚠️  Instalación interrumpida por el usuario")
            self.logger.warning("Instalación interrumpida por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ Error monitoreando instalación: {str(e)}")
            self.logger.error(f"Error monitoreando instalación: {str(e)}")
            return False

    def _get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado actual de la tarea.
        """
        try:
            response = requests.get(
                f"{self.serverUrl}/Task/{task_id}",
                headers={'Accept': 'application/fhir+json'}
            )

            if response.status_code != 200:
                print(f"\n❌ Error obteniendo estado: {response.status_code}")
                self.logger.error(f"Error obteniendo estado: {response.status_code}")
                return None

            return response.json()

        except Exception as e:
            self.logger.error(f"Error obteniendo estado: {str(e)}")
            return None

    def _display_progress(self, task: Dict[str, Any], previous_progress: int) -> int:
        """
        Muestra el progreso de la instalación.
        """
        status = task.get('status', 'unknown')
        progress = 0
        message = "Procesando..."
        
        # Intentar obtener progreso de los outputs
        for output in task.get('output', []):
            if output.get('type', {}).get('text') == 'progress':
                progress = int(float(output.get('valueDecimal', 0)))
            elif output.get('type', {}).get('text') == 'message':
                message = output.get('valueString', message)

        # Si no hay progreso pero hay estado, usar valores aproximados
        if progress == 0 and status != 'unknown':
            if status == 'in-progress':
                progress = 50
            elif status == 'completed':
                progress = 100

        # Solo mostrar si el progreso cambió
        if progress != previous_progress:
            bar_width = 40
            filled = int(bar_width * progress / 100)
            bar = '█' * filled + '░' * (bar_width - filled)
            print(f"\r⏳ Progreso: [{bar}] {progress}% {message}", end='')
            sys.stdout.flush()

        return progress

    def _show_completion_status(self, success: bool):
        """
        Muestra el estado final de la instalación.
        """
        end_time = datetime.now()
        duration = end_time - self.start_time
        duration_str = str(duration).split('.')[0]  # Remover microsegundos

        print("\n" + "=" * 50)
        if success:
            print(f"\n✅ Instalación completada exitosamente")
        else:
            print(f"\n❌ La instalación falló")
        print(f"⏱️  Tiempo total: {duration_str}")
        print("=" * 50 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='HAPI FHIR Implementation Guide Installer',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--serverUrl', 
                       required=True, 
                       help='URL del servidor HAPI FHIR\n' + 
                            'Ejemplo: http://localhost:8080/fhir')
    parser.add_argument('--pkg', 
                       required=True,
                       help='Ruta al archivo del paquete NPM (.tgz)\n' + 
                            'Ejemplo: ./my-implementation-guide.tgz')
    
    args = parser.parse_args()
    
    installer = HAPIImplementationGuideInstaller(args.serverUrl)
    success = installer.install_implementation_guide(args.pkg)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()