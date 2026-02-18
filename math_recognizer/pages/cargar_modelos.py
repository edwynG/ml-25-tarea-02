import reflex as rx

from math_recognizer.components.navbar import navbar
from math_recognizer.components.footer import footer
from math_recognizer.state.model_state import ModelState


@rx.page(route="/cargar-modelos", title="Cargar Modelos", on_load=ModelState.load_available_models)
def cargar_modelos() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.center(
                rx.vstack(
                    # Header
                    rx.center(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("upload", size=26, color="#f97316"),
                                rx.heading("Cargar Modelos", size="6", weight="bold", color="white"),
                                spacing="2", align="center",
                            ),
                            rx.text(
                                "Sube los modelos de Machine Learning que entrenaste en tus notebooks. "
                                "Necesitas al menos dos: uno para digitos y otro para operadores.",
                                size="2", color="#aaa", text_align="center", line_height="1.5",
                            ),
                            spacing="2", align="center",
                        ),
                        padding_top="1.5em", width="100%",
                    ),
                    # Upload area
                    rx.box(
                        rx.vstack(
                            rx.text("Subir modelo", size="3", weight="bold", color="white"),
                            rx.text(
                                "Formatos aceptados: .joblib, .pickle, .pkl, .h5, .keras",
                                size="1", color="#888",
                            ),
                            rx.upload(
                                rx.center(
                                    rx.vstack(
                                        rx.icon("cloud-upload", size=36, color="#666"),
                                        rx.text("Arrastra archivos aqui o haz clic", size="2", color="#aaa"),
                                        rx.text("Maximo 1 archivo a la vez", size="1", color="#888"),
                                        align="center", spacing="2",
                                    ),
                                    padding_y="2em",
                                ),
                                id="model_upload",
                                accept={
                                    "application/octet-stream": [".joblib", ".pickle", ".pkl", ".h5", ".keras"],
                                },
                                max_files=1,
                                border="2px dashed #444",
                                border_radius="12px",
                                width="100%",
                                cursor="pointer",
                                _hover={"border_color": "rgba(44, 83, 209, 0.4)", "background": "rgba(44, 83, 209, 0.05)"},
                                transition="all 0.15s ease",
                            ),
                            rx.button(
                                rx.icon("upload", size=14), "Subir Modelo",
                                on_click=ModelState.handle_upload(rx.upload_files(upload_id="model_upload")),
                                size="2", width="100%",
                            ),
                            rx.cond(
                                ModelState.upload_message != "",
                                rx.callout(ModelState.upload_message, icon="check", color_scheme="green", size="1", width="100%"),
                            ),
                            spacing="3",
                        ),
                        background="#12121a",
                        border="1px solid #333",
                        border_radius="12px",
                        padding="1.5em",
                        width="100%",
                    ),
                    # Installed models
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("folder-open", size=18, color="#888"),
                                rx.text("Modelos disponibles", size="3", weight="bold", color="white"),
                                spacing="2", align="center",
                            ),
                            rx.cond(
                                ModelState.model_info_list.length() > 0,  # type: ignore
                                rx.vstack(
                                    rx.foreach(
                                        ModelState.model_info_list,
                                        lambda pair: rx.hstack(
                                            rx.vstack(
                                                rx.hstack(
                                                    rx.icon("file-box", size=14, color="#4c8bf5"),
                                                    rx.text(pair[0], size="2", weight="bold", color="white"),
                                                    spacing="2", align="center",
                                                ),
                                                rx.cond(
                                                    pair[1] != "",
                                                    rx.text(pair[1], size="1", color="#888"),
                                                ),
                                                spacing="1",
                                                flex="1",
                                            ),
                                            rx.icon_button(
                                                rx.icon("trash-2", size=12),
                                                on_click=ModelState.delete_model(pair[0]),
                                                size="1", variant="ghost", color_scheme="red",
                                            ),
                                            spacing="2", align="center", width="100%",
                                            padding_y="0.25em",
                                            padding_left="0.5em",
                                            border_left="2px solid rgba(44, 83, 209, 0.4)",
                                        ),
                                    ),
                                    spacing="2", width="100%",
                                ),
                                rx.center(
                                    rx.text("No hay modelos cargados todavia.", size="2", color="#888"),
                                    padding_y="1em",
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
                    max_width="500px",
                    padding_x="1.5em",
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
