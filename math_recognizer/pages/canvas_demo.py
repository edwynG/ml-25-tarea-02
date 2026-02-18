import reflex as rx

from math_recognizer.components.navbar import navbar
from math_recognizer.components.footer import footer
from math_recognizer.state.mnist_state import MnistState


def _stat_box(label: str, value: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(label, size="1", color="#888"),
            rx.text(value, size="4", weight="bold", color="#4c8bf5"),
            spacing="0", align="center",
        ),
        background="#12121a",
        border="1px solid #333",
        border_radius="12px",
        padding="1em",
    )


@rx.page(route="/canvas-demo", title="MNIST Dataset Explorer", on_load=MnistState.load_initial)
def canvas_demo() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.center(
                rx.vstack(
                    rx.center(
                        rx.hstack(
                            rx.icon("database", size=26, color="#f97316"),
                            rx.heading("MNIST Dataset Explorer", size="6", weight="bold", color="white"),
                            spacing="2", align="center",
                        ),
                        padding_top="1.5em", width="100%",
                    ),

                    rx.box(
                        rx.vstack(
                            rx.text(
                                "El dataset MNIST contiene 70,000 imagenes de digitos escritos a mano "
                                "(60,000 entrenamiento + 10,000 prueba). Cada imagen es de 28x28 pixeles "
                                "en escala de grises. Este es el dataset que tu modelo de digitos debe aprender.",
                                size="2", color="#aaa", line_height="1.5",
                            ),
                            # Stats row
                            rx.flex(
                                _stat_box("Entrenamiento", "60,000"),
                                _stat_box("Prueba", "10,000"),
                                _stat_box("Clases", "0 - 9"),
                                _stat_box("Tamano", "28x28"),
                                gap="3", wrap="wrap", justify="center", width="100%",
                            ),
                            rx.box(width="100%", height="1px", background="#333"),
                            # Controls
                            rx.flex(
                                rx.vstack(
                                    rx.text("Dataset", size="1", color="#888"),
                                    rx.select(
                                        ["train", "test"],
                                        value=MnistState.dataset_split,
                                        on_change=MnistState.set_split,
                                        size="2",
                                    ),
                                    spacing="1",
                                ),
                                rx.vstack(
                                    rx.hstack(
                                        rx.text("Indice:", size="1", color="#888"),
                                        rx.badge(MnistState.image_index, variant="soft", size="1"),
                                        spacing="1", align="center",
                                    ),
                                    rx.slider(
                                        default_value=0, min=0,
                                        max=MnistState.max_index,
                                        on_value_commit=MnistState.set_index,
                                        width="100%",
                                    ),
                                    spacing="1", flex="1", min_width="200px",
                                ),
                                gap="4", wrap="wrap", align="end", width="100%",
                            ),
                            # Image display
                            rx.cond(
                                MnistState.current_image_b64 != "",
                                rx.center(
                                    rx.hstack(
                                        rx.box(
                                            rx.image(
                                                src=MnistState.current_image_b64,
                                                width="168px", height="168px",
                                                style={"imageRendering": "pixelated"},
                                            ),
                                            border="2px solid #444",
                                            border_radius="8px",
                                            overflow="hidden",
                                            background="black",
                                        ),
                                        rx.vstack(
                                            rx.vstack(
                                                rx.text("Label (clase real)", size="1", color="#888"),
                                                rx.heading(MnistState.image_label, size="7", weight="bold", color="#4c8bf5"),
                                                spacing="0",
                                            ),
                                            rx.vstack(
                                                rx.text("Dimensiones", size="1", color="#888"),
                                                rx.text(MnistState.image_shape, size="2", color="white"),
                                                spacing="0",
                                            ),
                                            rx.vstack(
                                                rx.text("Split", size="1", color="#888"),
                                                rx.badge(MnistState.dataset_split, size="2", variant="surface"),
                                                spacing="0",
                                            ),
                                            spacing="3",
                                        ),
                                        spacing="5", align="center",
                                    ),
                                    width="100%",
                                ),
                            ),
                            spacing="3",
                        ),
                        background="#12121a",
                        border="1px solid #333",
                        border_radius="12px",
                        padding="1.5em",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                    max_width="640px",
                    padding_x="1.5em",
                ),
                width="100%",
            ),
            width="100%",
            spacing="0",
            padding_bottom="4em",
        ),
        rx.box(
            footer(),
            position="sticky",
            bottom="0",
            width="100%",
            z_index="50",
        ),
        background="#0a0a0f",
        min_height="100vh",
        display="flex",
        flex_direction="column",
    )
