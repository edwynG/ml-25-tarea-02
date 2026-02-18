import reflex as rx

from math_recognizer.components.navbar import navbar
from math_recognizer.components.footer import footer
from math_recognizer.components.sketch_canvas import sketch_canvas
from math_recognizer.state.datagen_state import DatagenState


def _section_header(title: str, icon: str) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=14, color="#4c8bf5"),
        rx.text(title, font_size="0.85em", font_weight="700", color="white"),
        spacing="2",
        align_items="center",
        width="100%",
    )


def _section_divider() -> rx.Component:
    return rx.box(width="100%", height="1px", background="#333", margin_y="0.25em")


def _color_input(label: str, value, on_change) -> rx.Component:
    return rx.hstack(
        rx.text(label, size="1", color="#888", white_space="nowrap"),
        rx.el.input(
            type="color", value=value, on_change=on_change,
            width="24px", height="24px", cursor="pointer",
            style={"border": "none", "padding": "0", "background": "none"},
        ),
        spacing="2", align="center",
    )


def _header_box() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("brush", size=22, color="#4c8bf5"),
                rx.text(
                    "Generador de Datos",
                    font_size="1.1em",
                    font_weight="800",
                    color="white",
                ),
                spacing="2",
                align_items="center",
            ),
            rx.text(
                "Dibuja operadores o dígitos y descarga las imágenes "
                "para construir tu dataset de entrenamiento.",
                font_size="0.8em",
                color="#aaa",
                line_height="1.4",
            ),
            spacing="2",
            align_items="flex-start",
        ),
        background="linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%)",
        border="1px solid rgba(44, 83, 209, 0.25)",
        border_radius="12px",
        padding="1em",
        width="100%",
    )


def _control_panel() -> rx.Component:
    return rx.vstack(
        _header_box(),

        _section_header("Herramientas de Dibujo", "pencil"),
        rx.vstack(
            rx.hstack(
                rx.text("Grosor trazo:", font_size="0.8em", color="#aaa"),
                rx.slider(
                    default_value=8, min=1, max=20, step=1,
                    on_value_commit=DatagenState.update_stroke_width,
                    width="100px",
                ),
                rx.badge(DatagenState.stroke_width, variant="surface", size="1"),
                spacing="2", align="center",
            ),
            rx.hstack(
                _color_input("Trazo", DatagenState.stroke_color, DatagenState.set_stroke_color),  # type: ignore
                _color_input("Fondo", DatagenState.canvas_bg_color, DatagenState.set_canvas_bg_color),  # type: ignore
                spacing="4", align="center",
            ),
            spacing="3", width="100%",
        ),

        _section_divider(),

        _section_header("Resolución de descarga", "ruler"),
        rx.vstack(
            rx.hstack(
                rx.slider(
                    default_value=280, min=28, max=560, step=28,
                    on_value_commit=DatagenState.update_resolution,
                    width="100%",
                ),
                spacing="2", align="center", width="100%",
            ),
            rx.hstack(
                rx.badge(
                    DatagenState.resolution_label,
                    variant="surface", size="2", color_scheme="blue",
                ),
                spacing="2", align="center",
            ),
            rx.text(
                "Recomendado: 280×280 (10× MNIST). Mínimo: 28×28.",
                font_size="0.7em", color="#666", font_style="italic",
            ),
            spacing="2", width="100%",
        ),

        _section_divider(),

        _section_header("Acciones", "download"),
        rx.vstack(
            rx.button(
                rx.icon("download", size=14), "Descargar imagen",
                on_click=DatagenState.download_image,
                size="2", color_scheme="green", width="100%",
            ),
            rx.button(
                rx.icon("trash-2", size=14), "Limpiar",
                on_click=DatagenState.clear_canvas,
                size="2", color_scheme="red", variant="outline", width="100%",
            ),
            spacing="2", width="100%",
        ),

        width="100%",
        spacing="3",
        background="#12121a",
        border="1px solid #333",
        border_radius="12px",
        padding="1.25em",
    )


def _canvas_area() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.center(
                rx.vstack(
                    rx.text(
                        "Canvas",
                        font_size="0.85em", font_weight="600", color="#888",
                    ),
                    rx.box(
                        sketch_canvas(
                            canvas_id="datagen",
                            width="100%",
                            height="100%",
                            stroke_width=DatagenState.stroke_width,
                            stroke_color=DatagenState.stroke_color,
                            canvas_color=DatagenState.canvas_bg_color,
                        ),
                        width="280px",
                        height="280px",
                        border_radius="8px",
                        overflow="hidden",
                        border="2px solid var(--blue-6)",
                    ),
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("undo-2", size=14),
                            on_click=rx.call_script("window.undoCanvas_datagen()"),
                            size="1", variant="ghost", color_scheme="gray",
                            title="Deshacer",
                        ),
                        rx.icon_button(
                            rx.icon("redo-2", size=14),
                            on_click=rx.call_script("window.redoCanvas_datagen()"),
                            size="1", variant="ghost", color_scheme="gray",
                            title="Rehacer",
                        ),
                        rx.icon_button(
                            rx.icon("trash-2", size=14),
                            on_click=DatagenState.clear_canvas,
                            size="1", variant="ghost", color_scheme="red",
                            title="Limpiar",
                        ),
                        spacing="2",
                        justify="center",
                    ),
                    align="center",
                    spacing="2",
                ),
                width="100%",
                padding="2em",
            ),
            background="#12121a",
            border="1px solid #333",
            border_radius="12px",
            width="100%",
        ),
        # Tip box
        rx.box(
            rx.hstack(
                rx.icon("lightbulb", size=14, color="#f59e0b"),
                rx.text(
                    "Dibuja un símbolo, descárgalo, limpia el canvas y repite. "
                    "Crea suficientes muestras por clase para entrenar tu modelo.",
                    font_size="0.8em", color="#aaa", line_height="1.5",
                ),
                spacing="2", align_items="flex-start",
            ),
            background="rgba(245, 158, 11, 0.05)",
            border="1px solid rgba(245, 158, 11, 0.2)",
            border_radius="10px",
            padding="1em",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


@rx.page(route="/generar-datos", title="Generador de Datos")
def generar_datos() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.flex(
                # Left: control panel
                rx.box(
                    _control_panel(),
                    width=["100%", "100%", "260px"],
                    min_width=["auto", "auto", "260px"],
                ),
                # Right: canvas
                rx.box(
                    _canvas_area(),
                    flex="1",
                    min_width="0",
                ),
                direction=rx.breakpoints(initial="column", md="row"),
                gap="2em",
                width="100%",
                align_items="flex-start",
                padding=["1em", "1em", "1.5em"],
                max_width="900px",
                margin="0 auto",
            ),
            rx.spacer(),
            footer(),
            min_height="100vh",
            width="100%",
            spacing="0",
        ),
        background="#0a0a0f",
    )
