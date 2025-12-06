# 1. Uso de FastAPI como Backend Framework

Date: 2025-12-06
Status: Accepted

## Contexto
Necesitamos construir una API de alto rendimiento para el e-commerce, con soporte nativo para asincronía y documentación automática.

## Decisión
Utilizaremos **FastAPI** (Python) en lugar de Django o Flask.

## Consecuencias
Positivas:
* Validación de datos automática con Pydantic.
* Documentación Swagger UI generada automáticamente.
* Alto rendimiento (Starlette).

Negativas:
* Menos "magia" incluida (auth, admin) comparado con Django, requiere implementación manual.