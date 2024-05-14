# Vetsoft

Aplicación web para veterinarias utilizada en la cursada 2024 de Ingeniería y Calidad de Software. UTN-FRLP

## Dependencias

-   python 3
-   Django
-   sqlite
-   playwright
-   ruff

Version actual de la imagen: 1.1

## Instalar dependencias

`pip install -r requirements.txt`

## Iniciar la Base de Datos

`python manage.py migrate`

## Iniciar app

`python manage.py runserver`

## Integrantes

- Salani Pablo
- Moretti Francisco
- Luna Esteban
- Zubik Tomas

## Correr con Docker

`docker compose -f "docker-compose.yml" up -d --build`

Para acceder, abrir el navegador y buscar `localhost:8000`