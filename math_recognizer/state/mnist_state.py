import base64
import io
from functools import lru_cache

import numpy as np
import reflex as rx
from PIL import Image


@lru_cache(maxsize=1)
def _load_mnist():
    from keras.datasets import mnist
    return mnist.load_data()


class MnistState(rx.State):
    """State for the MNIST dataset viewer."""

    dataset_split: str = "train"
    image_index: int = 0
    current_image_b64: str = ""
    image_shape: str = ""
    image_label: str = ""
    max_index: int = 59999
    train_count: int = 60000
    test_count: int = 10000

    def set_split(self, split: str):
        self.dataset_split = split
        self.image_index = 0
        self.max_index = 59999 if split == "train" else 9999
        self._update_image()

    def set_index(self, value: list[int]):
        self.image_index = value[0] if isinstance(value, list) else value
        self._update_image()

    def _update_image(self):
        (x_train, y_train), (x_test, y_test) = _load_mnist()

        if self.dataset_split == "train":
            img_data = x_train[self.image_index]
            label = y_train[self.image_index]
        else:
            img_data = x_test[self.image_index]
            label = y_test[self.image_index]

        self.image_shape = f"{img_data.shape[0]}x{img_data.shape[1]} px, 1 canal (escala de grises)"
        self.image_label = str(int(label))

        img = Image.fromarray(img_data, mode="L")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        self.current_image_b64 = f"data:image/png;base64,{b64}"

    def load_initial(self):
        self._update_image()
