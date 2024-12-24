"""
Módulo de definición de modelos de datos para la API.

Este módulo define las estructuras de datos utilizadas en las solicitudes de la API.
Se utiliza Pydantic para validar y gestionar los datos recibidos.

Funcionalidades principales:
- Validación automática de los datos de entrada.
- Garantiza que las solicitudes contengan los campos requeridos.

Dependencias:
- pydantic (BaseModel): Framework para la validación y gestión de datos.
"""

from pydantic import BaseModel

class SolicitudConsulta(BaseModel):
    """
    Modelo de datos para las solicitudes de consulta.
    """
    user_name: str
    question: str