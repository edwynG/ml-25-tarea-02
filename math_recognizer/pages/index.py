import reflex as rx

from math_recognizer.components.navbar import navbar
from math_recognizer.components.footer import footer


def _feature_card(title: str, desc: str, href: str, icon: str, color: str) -> rx.Component:
    return rx.link(
        rx.box(
            rx.hstack(
                rx.center(
                    rx.icon(icon, size=24, color=color),
                    width="48px",
                    height="48px",
                    border_radius="12px",
                    background=f"color-mix(in srgb, {color} 12%, transparent)",
                    flex_shrink="0",
                ),
                rx.vstack(
                    rx.text(title, size="3", weight="bold", color="white"),
                    rx.text(desc, size="2", color="#aaa", line_height="1.4"),
                    spacing="1",
                ),
                spacing="4",
                align="center",
                width="100%",
            ),
            background="#12121a",
            border="1px solid #333",
            border_radius="12px",
            padding="1.25em",
            _hover={"border_color": "rgba(44, 83, 209, 0.4)", "transform": "translateY(-1px)"},
            transition="all 0.15s ease",
            cursor="pointer",
            width="100%",
        ),
        href=href,
        underline="none",
        width="100%",
    )


@rx.page(route="/", title="Dígitos")
def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.center(
                rx.vstack(
                    # Hero
                    rx.center(
                        rx.vstack(
                            rx.badge("Machine Learning", color_scheme="blue", size="2"),
                            rx.heading("Dígitos", size="8", weight="bold", color="white"),
                            rx.text(
                                "Reconoce expresiones matematicas dibujadas a mano "
                                "usando modelos de Machine Learning.",
                                size="3",
                                color="#aaa",
                                text_align="center",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        padding_y="3em",
                        width="100%",
                    ),
                    # Cards
                    _feature_card("A Jugar", "Dibuja digitos y operadores, evalua expresiones con tus modelos ML.", "/jugar", "gamepad-2", "#4c8bf5"),
                    _feature_card("Generador de Datos", "Dibuja simbolos y descarga imagenes para construir tu dataset de operadores.", "/generar-datos", "brush", "#a855f7"),
                    _feature_card("MNIST Dataset", "Explora el dataset MNIST para entender los datos de entrenamiento.", "/canvas-demo", "database", "#4ade80"),
                    _feature_card("Cargar Modelos", "Sube modelos de clasificacion (.joblib, .pickle, .h5).", "/cargar-modelos", "upload", "#f97316"),
                    # Separator
                    rx.box(
                        width="100%",
                        height="1px",
                        background="#333",
                        margin_y="1em",
                    ),
                    # Objective
                    rx.box(
                        rx.vstack(
                            rx.heading("Objetivo", size="5", weight="bold", color="white"),
                            rx.text(
                                "Evaluar una operacion matematica dibujando coeficientes, "
                                "exponentes y operadores en canvas individuales, y clasificarlos "
                                "con modelos de Machine Learning.",
                                color="#aaa",
                                line_height="1.6",
                            ),
                            rx.image(src="/img/canvas.png", width="100%", border_radius="12px"),
                            rx.text("Tres tipos de entrada:", weight="medium", size="3", color="white"),
                            rx.image(src="/img/canvas2.png", width="100%", border_radius="12px"),
                            rx.vstack(
                                rx.hstack(rx.badge("1", color_scheme="purple", variant="solid"), rx.text("Exponentes (morado): numeros del 0 al 9", size="2", color="#aaa"), align="center", spacing="2"),
                                rx.hstack(rx.badge("2", color_scheme="blue", variant="solid"), rx.text("Operadores (azul): +, -, *, /", size="2", color="#aaa"), align="center", spacing="2"),
                                rx.hstack(rx.badge("3", color_scheme="red", variant="solid"), rx.text("Numeros (rojo): numeros del 0 al 9", size="2", color="#aaa"), align="center", spacing="2"),
                                spacing="2",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        background="#12121a",
                        border="1px solid #333",
                        border_radius="12px",
                        padding="1.5em",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                    max_width="800px",
                    padding_x="1.5em",
                    padding_bottom="4em",
                    align="center",
                    margin_x="auto",
                ),
                width="100%",
            ),
            rx.spacer(),
            footer(),
            min_height="100vh",
            width="100%",
            spacing="0",
        ),
        background="#0a0a0f",
    )
