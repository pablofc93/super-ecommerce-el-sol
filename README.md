# Super Ecommerce El Sol

Sistema de comercio electrónico desarrollado con Django y Angular, que permite gestionar productos, categorías, clientes, usuarios, carritos, pedidos y pagos. El sistema incorpora además un panel administrativo, análisis de datos, segmentación de clientes y sistemas de recomendación.

## Tecnologías utilizadas

### Backend

* Python 3.13
* Django 5.2.8
* Django REST Framework
* SQLite
* Django CORS Headers
* Django Filters
* Simple JWT
* Scikit-learn
* NumPy
* SciPy
* Joblib
* Pillow
* Faker

### Frontend

* Angular
* TypeScript
* HTML
* CSS
* Bootstrap

### Herramientas

* Git
* Visual Studio Code

## Funcionalidades principales

### Cliente

* Registro e inicio de sesión.
* Visualización de productos.
* Consulta de productos por categorías.
* Visualización del detalle de productos.
* Carrito de compras.
* Realización de pedidos.
* Consulta de pedidos realizados.
* Consulta del historial de compras.
* Gestión del perfil.

### Administración

* Gestión de usuarios.
* Gestión de clientes.
* Gestión de productos.
* Gestión de categorías.
* Gestión de pedidos.
* Gestión de pagos.
* Panel administrativo.
* Panel de estadísticas.
* Visualización de indicadores y gráficos.
* Generación de reportes.
* Análisis de clientes.
* Segmentación de clientes mediante K-Means.
* Análisis de reglas de asociación mediante Apriori.
* Análisis de demanda.
* Análisis de productos más vendidos.
* Análisis de categorías.
* Sistema de recomendaciones.

## Estructura del proyecto

```text
super-ecommerce-el-sol/
│
├── backend/
│   ├── apps/
│   │   ├── adminpanel/
│   │   ├── analitica/
│   │   ├── clientes/
│   │   ├── pedidos/
│   │   ├── productos/
│   │   ├── recomendacion/
│   │   ├── reporting/
│   │   └── usuarios/
│   │
│   ├── ecommerce/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── media/
│   ├── static/
│   ├── templates/
│   ├── utils/
│   ├── .env.example
│   ├── manage.py
│   └── requirements.txt
│
├── docs/
│
├── frontend/
│   ├── src/
│   ├── angular.json
│   ├── package.json
│   └── package-lock.json
│
├── .gitignore
└── README.md
```

> Los archivos generados automáticamente o que contienen información sensible, como `.env`, `db.sqlite3` y `venv/`, están excluidos del repositorio mediante `.gitignore`.

## Requisitos

Para ejecutar el proyecto localmente se necesita:

* Python 3.13 o una versión compatible con las dependencias especificadas en `backend/requirements.txt`.
* Node.js y npm.
* Angular CLI.
* Git.

## Instalación

### 1. Clonar el repositorio

Desde una terminal, ubicarse en la carpeta donde se desea instalar el proyecto y ejecutar:

```bash
git clone https://github.com/pablofc93/super-ecommerce-el-sol.git
cd super-ecommerce-el-sol
```

> La rama principal del repositorio es `master`.

---

# Backend

## 2. Crear el entorno virtual

El entorno virtual se recomienda en la raíz del proyecto para mantener aisladas las dependencias de Python.

Desde la carpeta raíz:

```bash
python -m venv venv
```

### Windows

Activar el entorno virtual:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 3. Instalar las dependencias

Con el entorno virtual activado, acceder a la carpeta del backend:

```bash
cd backend
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene las dependencias utilizadas por el backend.

## 4. Configurar las variables de entorno

El backend utiliza variables de entorno para almacenar valores sensibles y configuraciones específicas de cada instalación.

El repositorio incluye un archivo de referencia:

```text
backend/.env.example
```

Crear una copia de este archivo con el nombre:

```text
backend/.env
```

El archivo `.env` debe contener las variables necesarias para ejecutar el proyecto.

Ejemplo:

```env
SECRET_KEY=tu_clave_secreta_de_django
DEBUG=True
```

La `SECRET_KEY` debe ser propia de cada instalación y nunca debe publicarse en el repositorio.

Para generar una nueva clave de Django:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar el valor generado en `backend/.env`:

```env
SECRET_KEY=clave_generada
DEBUG=True
```

El archivo `.env` está excluido mediante `.gitignore` y no debe subirse al repositorio.

> Cada desarrollador debe generar y utilizar su propia `SECRET_KEY`.

## 5. Inicializar la base de datos

El proyecto ofrece dos alternativas para disponer de una base de datos:

* **Alternativa A:** utilizar una copia de la base de datos SQLite completa previamente preparada.
* **Alternativa B:** crear la base de datos desde cero mediante las migraciones y los comandos de carga de datos.

---

### Alternativa A — Utilizar una base de datos SQLite existente

Esta alternativa permite disponer rápidamente de una base de datos completa con los datos de prueba previamente cargados.

Descargar `db.sqlite3` desde:

[Descargar base de datos SQLite](https://mega.nz/file/f5QBkZoZ#CxVA_bZ7eUmzYYwo_cSmCo29gdZZq1Q4KnJp20s4OMs)

El archivo contiene una copia de la base de datos del sistema con los datos de prueba previamente cargados.

#### Instalación

1. Descargar el archivo `db.sqlite3`.
2. Colocar el archivo descargado en:

```text
backend/db.sqlite3
```

Una vez colocado el archivo en esa ubicación, se dispondrá de la base de datos completa utilizada por el sistema.

> Esta alternativa permite evitar la ejecución de todos los comandos de generación de datos.

> La base de datos SQLite no se almacena directamente en el repositorio debido a su tamaño. Se proporciona externamente para facilitar la ejecución del proyecto con datos de prueba.

---

### Alternativa B — Crear la base de datos desde cero

Esta alternativa permite generar una instalación limpia de la base de datos mediante las migraciones y los comandos de carga incluidos en el backend.

Primero ejecutar las migraciones:

```bash
python manage.py migrate
```

Luego ejecutar los comandos de carga de datos respetando el orden indicado a continuación, debido a las relaciones existentes entre las diferentes entidades.

### Orden de carga de los datos

#### 1. Categorías

Genera las categorías utilizadas por los productos.

```bash
python manage.py seed_categorias
```

**Estado:** Cargado.

---

#### 2. Productos

Genera los productos utilizados por el sistema y los asocia con las categorías existentes.

```bash
python manage.py seed_productos
```

**Estado:** Cargado.

> Este comando debe ejecutarse después de `seed_categorias` y antes de los seeds que dependan de productos, como los correspondientes a carritos y pedidos.

---

#### 3. Usuarios

Genera los usuarios de prueba del sistema.

Para generar 2500 usuarios:

```bash
python manage.py seed_usuarios --cantidad 2500
```

**Estado:** Cargado.

---

#### 4. Clientes

Genera 2500 clientes asociados a usuarios existentes.

```bash
python manage.py seed_clientes --cantidad 2500
```

**Estado:** Cargado.

---

#### 5. Carritos

Genera 2500 carritos asociados a clientes existentes.

```bash
python manage.py seed_carritos --cantidad 2500
```

**Estado:** Cargado.

---

#### 6. Items del carrito

Genera los elementos asociados a los carritos y productos existentes.

```bash
python manage.py seed_carrito_items
```

**Estado:** Cargado.

---

#### 7. Pedidos

Genera 20000 pedidos.

```bash
python manage.py seed_pedidos --cantidad 20000
```

> Cada ejecución del comando genera otros 20000 pedidos.

**Estado:** Cargado.

---

#### 8. Items del pedido

Genera los elementos correspondientes a los pedidos y productos existentes.

```bash
python manage.py seed_pedidoitems
```

**Estado:** Cargado.

---

#### 9. Pagos

Genera los pagos asociados a los pedidos existentes.

```bash
python manage.py seed_pagos
```

**Estado:** Cargado.

---

#### 10. Compras

Genera las compras correspondientes a los datos existentes.

```bash
python manage.py seed_compras
```

**Estado:** Cargado.

---

#### 11. Analítica

Genera o actualiza los datos utilizados por los módulos de análisis del sistema.

```bash
python manage.py actualizar_analitica
```

**Estado:** Cargado.

> La generación de la analítica debe realizarse después de disponer de usuarios, clientes, productos, pedidos, items de pedidos, pagos y compras.

### Resumen del orden

| Orden | Tabla / módulo    | Comando                | Estado  |
| ----: | ----------------- | ---------------------- | ------- |
|     1 | Categorías        | `seed_categorias`      | Cargado |
|     2 | Productos         | `seed_productos`       | Cargado |
|     3 | Usuarios          | `seed_usuarios`        | Cargado |
|     4 | Clientes          | `seed_clientes`        | Cargado |
|     5 | Carritos          | `seed_carritos`        | Cargado |
|     6 | Items del carrito | `seed_carrito_items`   | Cargado |
|     7 | Pedidos           | `seed_pedidos`         | Cargado |
|     8 | Items del pedido  | `seed_pedidoitems`     | Cargado |
|     9 | Pagos             | `seed_pagos`           | Cargado |
|    10 | Compras           | `seed_compras`         | Cargado |
|    11 | Analítica         | `actualizar_analitica` | Cargado |

> **Importante:** el orden anterior corresponde al procedimiento utilizado para generar los datos de prueba del proyecto. Se recomienda respetarlo al realizar una instalación desde cero.

### Administrador

Para acceder al panel administrativo se necesita disponer de un usuario con permisos de administrador.

La creación o disponibilidad del usuario administrador depende de la configuración de la instalación.

**Estado:** Pendiente de documentar las credenciales y/o procedimiento de creación.

### Usuarios de prueba

Los usuarios y clientes de prueba pueden generarse mediante los comandos correspondientes.

Las credenciales de acceso se documentan en la sección [Usuarios de prueba](#usuarios-de-prueba).

## 6. Ejecutar el backend

Desde la carpeta `backend` y con el entorno virtual activado:

```bash
python manage.py runserver
```

Por defecto, el backend estará disponible en:

```text
http://127.0.0.1:8000/
```

---

# Frontend

## 7. Instalar las dependencias

Desde la carpeta raíz del proyecto:

```bash
cd frontend
npm install
```

Esto instalará las dependencias especificadas en `package.json`, utilizando las versiones registradas en `package-lock.json`.

## 8. Ejecutar Angular

Ejecutar:

```bash
ng serve
```

El frontend estará disponible normalmente en:

```text
http://localhost:4200/
```

## 9. Ejecutar el sistema completo

Para utilizar el sistema completo deben estar ejecutándose simultáneamente el backend y el frontend.

### Backend

En una terminal:

```bash
cd super-ecommerce-el-sol
venv\Scripts\activate
cd backend
python manage.py runserver
```

### Frontend

En otra terminal:

```bash
cd super-ecommerce-el-sol\frontend
npm install
ng serve
```

Luego acceder desde el navegador a:

```text
http://localhost:4200/
```

---

## Variables de entorno

Las variables sensibles o específicas del entorno no deben almacenarse directamente en el repositorio.

El backend utiliza:

```text
backend/.env
backend/.env.example
```

El archivo `.env.example` contiene las variables necesarias como referencia.

El archivo `.env` contiene los valores utilizados por la instalación local y está excluido mediante `.gitignore`.

Cada desarrollador debe crear su propio archivo `.env` a partir de `.env.example`.

---

## Base de datos

El proyecto utiliza SQLite como sistema gestor de base de datos.

El archivo:

```text
backend/db.sqlite3
```

está excluido del repositorio mediante `.gitignore`.

La base de datos puede obtenerse mediante dos alternativas:

1. Descargar la base de datos completa desde la sección [Alternativa A](#alternativa-a--utilizar-una-base-de-datos-sqlite-existente).
2. Crear la base de datos desde cero mediante las migraciones y los comandos de carga de datos descritos en la sección [Alternativa B](#alternativa-b--crear-la-base-de-datos-desde-cero).

---

## Imágenes de productos

Las imágenes utilizadas por los productos se almacenan externamente y no se incluyen directamente en el repositorio debido a su cantidad y tamaño.

### Descarga de las imágenes

Las imágenes se encuentran disponibles en un archivo comprimido `.rar`:

[Descargar imágenes de productos](https://mega.nz/file/P9Ykib7A#Hh3-crdHcVJEIsE_zJ57212eJYqqAH8JosxKGFq2hlc)

### Instalación de las imágenes

1. Descargar el archivo `.rar`.
2. Extraer su contenido.
3. Localizar la carpeta `productos`.
4. Copiar la carpeta `productos` dentro de:

```text
backend/media/
```

La estructura final debería quedar aproximadamente así:

```text
backend/
└── media/
    └── productos/
        ├── imagen1.jpg
        ├── imagen2.jpg
        └── ...
```

> Las imágenes no se almacenan directamente en el repositorio debido a su cantidad y tamaño.

---

## Documentación

La carpeta `docs/` contiene documentación adicional relacionada con el proyecto.

```text
docs/
```

En esta carpeta se pueden incorporar:

* Diagramas.
* Documentación técnica.
* Diagramas de arquitectura.
* Diagramas de base de datos.
* Decisiones de diseño.
* Documentación de análisis.
* Material complementario del proyecto.

---

## Análisis de datos

El proyecto incorpora diferentes técnicas de minería de datos y análisis, entre ellas:

* **K-Means:** segmentación de clientes.
* **Apriori:** descubrimiento de reglas de asociación.
* **Análisis de demanda.**
* **Análisis de productos más vendidos.**
* **Análisis de categorías.**
* **Generación de información para recomendaciones.**

La actualización de los datos utilizados por los módulos de analítica se realiza mediante:

```bash
python manage.py actualizar_analitica
```

---

## Usuarios de prueba

La instalación mediante seeds permite generar usuarios y clientes de prueba.

### Administrador

```text
Usuario: [PENDIENTE]
Contraseña: [PENDIENTE]
```

### Cliente

```text
Usuario: [PENDIENTE]
Contraseña: [PENDIENTE]
```

> Las credenciales de prueba deben modificarse en entornos reales y no deben utilizarse para instalaciones destinadas a producción.

---

## Estado del proyecto

El sistema se encuentra en desarrollo activo.

Las funcionalidades principales de comercio electrónico, administración y análisis se encuentran implementadas, mientras que determinados procesos auxiliares de generación de datos, documentación y configuración continúan en desarrollo.

---

## Licencia

Este proyecto fue desarrollado íntegramente por **Pablo Fabián Camacho**.

La información sobre la licencia de uso y distribución será incorporada posteriormente.
