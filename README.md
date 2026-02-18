# Tarea 2: Clasificación

## Objetivo

El objetivo de la tarea es habilitar la sección `A jugar` para que tengamos un panel como el siguiente:

![Canvas de imagen](assets/img/canvas.png)

en el cual podamos ejecutar una operación matemática sencilla y evaluar su resultado.

### El Canvas

Tenemos entonces tres tipos de input en nuestro canvas:

![Canvas de imagen](assets/img/canvas2.png)

1. Exponentes: 3 posibles referentes a los cuadrados morados. Deben ser números del 0 al 9.
2. Operadores: 2 posibles referentes a los cuadrados azules. Explicados en la siguiente sección.
3. Números: 3 posibles referentes a los cuadrados rojos. Deben ser números del 0 al 9.

## Modelo de operadores

### Datos de entrada

El dataset **debe** ser creado por ustedes! La cantidad de imágenes, estilo, resolución y cualquier elemento que consideren relevante debe ser decidido por ustedes: sean creativos. En el notebook referente al modelo de operadores, es necesaria una sección que explique toda la toma decisiones.

### Clases del modelo

Solo vamos a usar las 4 operaciones fundamentales: suma, resta, multiplicación y división.

En el caso de suma y resta las únicas opciones posibles son: + (ASCII Code 43) y - (ASCII Code 45), respectivamente.

En el caso de multiplicación y división tendremos 2 opciones como sigue:

### Multiplicación

Una x (ASCII Code 215) o un asterisco * (ASCII Code 42)

![Multiplicación 1](assets/img/mult1.png) ![Multiplicación 2](assets/img/mult2.png)

### División

Un slash / (ASCII code 47) o el operando convencional (ASCII code 247)

![División 1](assets/img/div2.png) ![División 2](assets/img/div1.png)

## Modelo de clasificación de números

### Datos de entrada

Ya disponible en el código

```python
from keras.datasets import mnist
from functools import lru_cache

@lru_cache(maxsize=1)
def get_mnist_data():
    return mnist.load_data()
```

Usaremos el dataset [mnist](http://www.pymvpa.org/datadb/mnist.html) con la interfaz de [Keras](https://keras.io/getting_started/) para facilitar consistencia en todos los proyectos.

### Sobre la evaluación del pipeline

1. En la sección `notebooks` deben crear uno o dos archivos `.ipynb` donde expliquen claramente todo el pipeline que usaron para crear los modelos, explicar el proceso de preprocesamiento, creación de datos (de ser necesario) y cualquier elemento que consideren relevante.
2. Los modelos asociados a la solución principal deben haber sido vistos en clase.
3. Los modelos **extras** que quisieran agregar para comparar rendimiento pueden no haber sido vistos en clases (redes neuronales convolucionales usando PyTorch por ejemplo)

## Ejemplos: cómo exportar y conectar tu modelo

### Guardar el modelo entrenado

Una vez que hayas entrenado tu modelo en el notebook, guárdalo con `joblib`:

```python
import joblib

# modelo = ...  (tu modelo ya entrenado)
joblib.dump(modelo, "mi_modelo_digitos.joblib")
```

Luego sube el archivo `.joblib` en la página **Cargar Modelos** de la app.

### Adaptar el preprocesamiento en la app

Edita `math_recognizer/utils/image_processing.py` para que los pasos coincidan **exactamente** con lo que hiciste en tu notebook. Por ejemplo, si entrenaste **sin ecualización y sin inversión**:

```python
def prepare_digit_image(image):
    gray = _to_grayscale(image)
    gray = _ensure_light_bg(gray)
    resized = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
    # sin equalizeHist, sin bitwise_not
    return resized
```

Si entrenaste **con umbral binario**:

```python
def prepare_digit_image(image):
    gray = _to_grayscale(image)
    gray = _ensure_light_bg(gray)
    resized = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
    equalized = cv2.equalizeHist(resized)
    _, binary = cv2.threshold(equalized, 127, 255, cv2.THRESH_BINARY)
    inverted = cv2.bitwise_not(binary)
    return inverted
```

### Formatos soportados

| Formato | Extensión | Librería |
|---------|-----------|----------|
| Joblib | `.joblib` | `joblib.dump(modelo, "archivo.joblib")` |
| Pickle | `.pkl`, `.pickle` | `joblib.dump(modelo, "archivo.pkl")` |
| Keras | `.h5`, `.keras` | `modelo.save("archivo.h5")` |

### Modelos compatibles (scikit-learn)

Cualquier clasificador de scikit-learn funciona sin modificar el código de la app:

- `KNeighborsClassifier` — soporta `predict_proba()` automáticamente
- `SVC` / `NuSVC` — la app usa `decision_function()` como fallback si no tiene `predict_proba()`
- `LinearSVC` — igual que SVC, usa `decision_function()`
- `RandomForestClassifier`, `DecisionTreeClassifier`, `GaussianNB`, `MLPClassifier`, etc.

## Comentarios

### Sobre el framework de la aplicación

El código está hecho en [Reflex](https://reflex.dev/) un framework para desarrollar aplicaciones web completas en Python.

La [Documentación](https://reflex.dev/docs/) de Reflex es bastante sencilla de entender y la mayoría de funcionalidades necesarias ya están implementadas.

### Cómo ejecutar la aplicación

#### Desarrollo local

1. `pip install -r requirements.txt` instala las dependencias
2. `reflex init` inicializa el proyecto
3. `reflex run` ejecuta la aplicación en `http://localhost:3000`

#### Docker

1. `docker compose build` crea el contenedor
2. `docker compose up` lo ejecuta en modo desarrollador
3. `docker compose up -d` lo ejecuta modo daemon

### Sobre las operaciones

1. Asumimos que la aplicación siempre será usada por un agente honesto. No se debe validar para datos que no sean los referentes al modelo (aunque es un problema interesante de resolver)
2. Somos consistentes en la entrada de cada canvas así como en el orden de las operaciones: de izquierda a derecha y con prioridad de operadores: ^, ( *, /), (+, -).

### Sobre la parte visual

La aplicación tiene las siguientes páginas:

1. **Inicio** (`/`): Página principal con instrucciones
2. **A Jugar** (`/jugar`): Panel con 8 canvas (3 números, 3 exponentes, 2 operadores) para evaluar expresiones
3. **MNIST** (`/canvas-demo`): Explorador del dataset MNIST
4. **Cargar Modelos** (`/cargar-modelos`): Carga de modelos ML (.joblib, .pickle)

### Estructura del proyecto

```
math_recognizer/          # Paquete principal de la app Reflex
  state/                  # Clases de estado (canvas, game, model, mnist)
  components/             # Componentes reutilizables (canvas, navbar)
  pages/                  # Páginas de la aplicación
  utils/                  # Utilidades (procesamiento de imagen)
assets/                   # Recursos estáticos (imágenes, JS)
models/                   # Modelos ML (input/output)
backup/                   # Archivos Streamlit originales (referencia)
```
