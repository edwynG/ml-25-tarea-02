import cv2
import numpy as np


def transform_image_to_mnist(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Transform a canvas export image to MNIST-compatible 28x28 format.

    Matches MNIST conventions:
    - 28x28 grayscale
    - Background = 0 (black)
    - Digit/symbol strokes = white (up to 255)
    - Content is cropped and centered with padding (like MNIST)
    - Soft anti-aliased edges preserved (no binary thresholding)

    Args:
        image: Input image as numpy array (H, W, C) — RGB from PIL.

    Returns:
        Tuple of (processed_image, equalized_image) both 28x28 uint8.
    """
    # Remove alpha channel if present
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = image[:, :, :3]

    # Convert RGB to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    # Determine if strokes are lighter or darker than background.
    # Sample corners to estimate background value.
    h, w = gray.shape
    corners = [gray[0, 0], gray[0, w - 1], gray[h - 1, 0], gray[h - 1, w - 1]]
    bg_value = int(np.median(corners))

    # Make background black, strokes white (like MNIST)
    if bg_value > 127:
        # Light background, dark strokes → invert
        gray = 255 - gray
    else:
        # Dark background, light strokes → subtract background
        gray = gray.astype(np.int16) - bg_value
        gray = np.clip(gray, 0, 255).astype(np.uint8)

    # Crop to bounding box of the drawn content (non-zero pixels)
    # This ensures the digit fills the frame like MNIST digits do.
    threshold = 20  # ignore faint noise
    coords = np.argwhere(gray > threshold)

    if coords.size == 0:
        # Nothing drawn — return blank 28x28
        blank = np.zeros((28, 28), dtype=np.uint8)
        return blank, blank

    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    # Extract the content region
    cropped = gray[y_min:y_max + 1, x_min:x_max + 1]

    # Fit into a square (MNIST digits are centered in a square)
    ch, cw = cropped.shape
    side = max(ch, cw)
    square = np.zeros((side, side), dtype=np.uint8)
    y_offset = (side - ch) // 2
    x_offset = (side - cw) // 2
    square[y_offset:y_offset + ch, x_offset:x_offset + cw] = cropped

    # Add padding (~4px equivalent at 28x28 = ~14% border, matching MNIST)
    pad = max(side // 6, 2)
    padded = np.zeros((side + 2 * pad, side + 2 * pad), dtype=np.uint8)
    padded[pad:pad + side, pad:pad + side] = square

    # Resize to 28x28 with anti-aliasing preserved
    resized = cv2.resize(padded, (28, 28), interpolation=cv2.INTER_AREA)

    # Equalized version
    equalized = cv2.equalizeHist(resized)

    return resized, equalized


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an image to grayscale, removing alpha if present."""
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = image[:, :, :3]
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image.copy()


def _ensure_light_bg(gray: np.ndarray) -> np.ndarray:
    """Ensure the image has a light background with dark strokes.

    The student's models were trained with a light canvas (#eee) and dark strokes.
    Our Reflex canvas may use dark bg + light strokes. This normalises both cases
    to light-background format before the student's pipeline runs.
    """
    h, w = gray.shape
    corners = [gray[0, 0], gray[0, w - 1], gray[h - 1, 0], gray[h - 1, w - 1]]
    bg_value = int(np.median(corners))
    if bg_value < 128:
        # Dark background → invert so it becomes light background with dark strokes
        return cv2.bitwise_not(gray)
    return gray

# UCV: Los dos métodos que podemos cambiar en el caso de cambiar el preprocesamiento.

def prepare_digit_image(image: np.ndarray) -> np.ndarray:
    """Preprocesa la imagen del canvas para el modelo de digitos.

    Pipeline por defecto:
    normalizar fondo claro -> resize 28x28 -> equalizeHist -> invertir (bitwise_not)

    Retorna un array uint8 de 28x28.
    """
    # PASO 1: Convertir a escala de grises
    #   El canvas nos da una imagen RGB; nuestros modelos esperan un solo canal.
    gray = _to_grayscale(image)

    # PASO 2: Normalizar fondo
    #   Asegura que siempre empecemos con fondo claro y trazos oscuros,
    #   sin importar el esquema de colores del canvas.
    gray = _ensure_light_bg(gray)

    # PASO 3: Redimensionar al tamaño de entrada del modelo
    #   En el caso de que cambien la resolución, NO recomendado porque deben cambiar toda el app.
    #   Cambia la interpolación si usaste otra durante el entrenamiento
    #   (ej. cv2.INTER_LINEAR, cv2.INTER_CUBIC).
    resized = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)

    # PASO 4: Ecualización de histograma
    #   Mejora el contraste. Elimina esta línea si NO usan equalizeHist
    #   durante el entrenamiento.
    equalized = cv2.equalizeHist(resized)

    # PASO 5: Invertir colores (bitwise_not)
    #   después de esto: fondo=negro (0), trazos=blanco (255) — estilo MNIST.
    #   Elimina esta línea si tu modelo espera imagenes con fondo claro.
    inverted = cv2.bitwise_not(equalized)

    return inverted


# Modificaciones comunes para prepare_digit_image():
# - Omitir ecualización:        elimina o comenta la línea del PASO 4.
# - Omitir inversión:           elimina o comenta la línea del PASO 5.
# - Agregar umbral binario:     después del PASO 4 (o PASO 3), agrega:
#       _, result = cv2.threshold(equalized, 127, 255, cv2.THRESH_BINARY)
# - Cambiar interpolación:      en el PASO 3, reemplaza cv2.INTER_AREA por
#       cv2.INTER_LINEAR o cv2.INTER_CUBIC.
# - Diferente tamaño objetivo:  en el PASO 3, cambia (28, 28) por ej. (32, 32).
# - Agregar desenfoque gaussiano: después del PASO 3, agrega:
#       resized = cv2.GaussianBlur(resized, (3, 3), 0)

# UCV: Los dos métodos que podemos cambiar en el caso de cambiar el preprocesamiento.

def prepare_operator_image(image: np.ndarray) -> np.ndarray:
    """Preprocesa la imagen del canvas para el modelo de operadores.

    Pipeline por defecto:
    normalizar fondo claro -> resize 28x28 -> equalizeHist (SIN inversión)

    Retorna un array uint8 de 28x28.
    """
    # PASO 1: Convertir a escala de grises
    #   El canvas nos da una imagen RGB; nuestros modelos esperan un solo canal.
    gray = _to_grayscale(image)

    # PASO 2: Normalizar fondo
    #   Asegura que siempre empecemos con fondo claro y trazos oscuros,
    #   sin importar el esquema de colores del canvas.
    gray = _ensure_light_bg(gray)

    # PASO 3: Redimensionar al tamaño de entrada del modelo
    #   Cambia (28, 28) si tu modelo espera otra resolucion.
    #   Cambia la interpolación si usaste otra durante el entrenamiento
    #   (ej. cv2.INTER_LINEAR, cv2.INTER_CUBIC).
    resized = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)

    # PASO 4: Ecualizacion de histograma
    #   Mejora el contraste. Elimina esta linea si NO ecualizaste
    #   durante el entrenamiento.
    equalized = cv2.equalizeHist(resized)

    return equalized


# Modificaciones comunes para prepare_operator_image():
# - Omitir ecualización:        elimina o comenta la línea del PASO 4,
#                                y retorna `resized` en su lugar.
# - Agregar inversión:          después del PASO 4, agrega:
#       equalized = cv2.bitwise_not(equalized)
# - Agregar umbral binario:     después del PASO 4 (o PASO 3), agrega:
#       _, result = cv2.threshold(equalized, 127, 255, cv2.THRESH_BINARY)
# - Cambiar interpolación:      en el PASO 3, reemplaza cv2.INTER_AREA por
#       cv2.INTER_LINEAR o cv2.INTER_CUBIC.
# - Diferente tamaño objetivo:  en el PASO 3, cambia (28, 28) por ej. (32, 32).
# - Agregar blur gaussiano: después del PASO 3, agrega:
#       resized = cv2.GaussianBlur(resized, (3, 3), 0)
