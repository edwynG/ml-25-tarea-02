import reflex as rx

from math_recognizer.components.navbar import navbar
from math_recognizer.components.footer import footer
from math_recognizer.components.sketch_canvas import sketch_canvas
from math_recognizer.state.canvas_state import CanvasState
from math_recognizer.state.game_state import GameState
from math_recognizer.state.model_state import ModelState


def _section_header(title: str, icon: str) -> rx.Component:
    """Section header inside the left panel."""
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


def _op_input(value, on_change, placeholder: str, title: str) -> rx.Component:
    return rx.el.input(
        value=value, on_change=on_change,
        placeholder=placeholder, max_length=1, title=title,
        style={
            "width": "28px", "text_align": "center", "padding": "2px",
            "background": "#1a1a2e", "border": "1px solid #444",
            "border_radius": "4px", "color": "white", "font_size": "12px",
        },
    )


def _header_box() -> rx.Component:
    """Title box at the top of the panel, like formula_box in ml-playground."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("gamepad-2", size=22, color="#4c8bf5"),
                rx.text(
                    "A Jugar!",
                    font_size="1.1em",
                    font_weight="800",
                    color="white",
                ),
                spacing="2",
                align_items="center",
            ),
            rx.text(
                "Dibuja en los canvas, selecciona tus modelos y pulsa Evaluar.",
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
    """Left side panel with controls organized by section."""
    return rx.vstack(
        # Title box
        _header_box(),
        # Panel header with collapse button
        rx.hstack(
            rx.text("Controles", font_size="0.95em", font_weight="700", color="white"),
            rx.spacer(),
            rx.box(
                rx.icon("panel-left-close", size=16, color="#999"),
                padding="0.3em",
                cursor="pointer",
                border_radius="6px",
                _hover={"background": "rgba(255, 255, 255, 0.05)", "color": "white"},
                on_click=GameState.set_show_panel(False),  # type: ignore
            ),
            width="100%",
            align_items="center",
        ),
        _section_divider(),
        
        _section_header("Herramientas de Dibujo", "pencil"),
        rx.vstack(
            rx.hstack(
                rx.text("Grosor:", font_size="0.8em", color="#aaa"),
                rx.slider(
                    default_value=3, min=1, max=10, step=1,
                    on_value_commit=CanvasState.update_stroke_width,
                    width="80px",
                ),
                rx.badge(CanvasState.stroke_width, variant="surface", size="1"),
                spacing="2", align="center",
            ),
            rx.hstack(
                _color_input("Trazo", CanvasState.stroke_color, CanvasState.set_stroke_color),  # type: ignore
                _color_input("Fondo", CanvasState.canvas_bg_color, CanvasState.set_canvas_bg_color),  # type: ignore
                spacing="4", align="center",
            ),
            spacing="3", width="100%",
        ),

        _section_divider(),

        _section_header("Modelos", "brain"),
        rx.vstack(
            rx.vstack(
                rx.text("Modelo dígitos", font_size="0.8em", color="#aaa"),
                rx.select(
                    ModelState.available_models,
                    placeholder="Seleccionar...",
                    value=ModelState.selected_digit_model,
                    on_change=ModelState.set_digit_model,
                    size="1",
                    width="100%",
                ),
                spacing="1", width="100%",
            ),
            rx.vstack(
                rx.text("Modelo operadores", font_size="0.8em", color="#aaa"),
                rx.select(
                    ModelState.available_models,
                    placeholder="Seleccionar...",
                    value=ModelState.selected_operator_model,
                    on_change=ModelState.set_operator_model,
                    size="1",
                    width="100%",
                ),
                spacing="1", width="100%",
            ),
            spacing="3", width="100%",
        ),

        _section_divider(),

        _section_header("Etiquetas Operadores", "tags"),
        rx.text(
            "Mapeo clase → símbolo",
            font_size="0.75em", color="#666", font_style="italic",
        ),
        rx.flex(
            _op_input(GameState.op_label_0, GameState.set_op_label_0, "0:+", "Clase 0"),
            _op_input(GameState.op_label_1, GameState.set_op_label_1, "1:-", "Clase 1"),
            _op_input(GameState.op_label_2, GameState.set_op_label_2, "2:x", "Clase 2"),
            _op_input(GameState.op_label_3, GameState.set_op_label_3, "3:*", "Clase 3"),
            _op_input(GameState.op_label_4, GameState.set_op_label_4, "4:÷", "Clase 4"),
            _op_input(GameState.op_label_5, GameState.set_op_label_5, "5:/", "Clase 5"),
            gap="2", wrap="wrap",
        ),

        _section_divider(),

        _section_header("Acciones", "play"),
        rx.vstack(
            rx.button(
                rx.icon("play", size=14), "Evaluar",
                on_click=GameState.evaluate_expression,
                size="2", color_scheme="green", width="100%",
                loading=GameState.is_loading,
            ),
            rx.button(
                rx.icon("download", size=14), "Descargar",
                on_click=[GameState.export_all_canvases, GameState.download_canvases],
                size="2", variant="soft", width="100%",
            ),
            rx.button(
                rx.icon("trash-2", size=14), "Limpiar Todo",
                on_click=GameState.clear_all_canvases,
                size="2", color_scheme="red", variant="outline", width="100%",
            ),
            spacing="2", width="100%",
        ),

        _section_divider(),

        rx.hstack(
            rx.switch(
                checked=GameState.show_debug,
                on_change=GameState.set_show_debug,
                size="1",
            ),
            rx.text("Debug", font_size="0.8em", color="#aaa"),
            spacing="2", align_items="center",
        ),

        # Panel styling
        width="100%",
        spacing="3",
        background="#12121a",
        border="1px solid #333",
        border_radius="12px",
        padding="1.25em",
    )


def _canvas_tile(
    canvas_id: str,
    label: str,
    prediction: rx.Var[str],
    color_scheme: str,
    w: str,
    h: str,
) -> rx.Component:
    """Single labeled canvas with prediction underneath."""
    return rx.vstack(
        rx.badge(label, color_scheme=color_scheme, size="1", variant="surface"),
        rx.box(
            sketch_canvas(
                canvas_id=canvas_id, width="100%", height="100%",
                stroke_width=CanvasState.stroke_width,
                stroke_color=CanvasState.stroke_color,
                canvas_color=CanvasState.canvas_bg_color,
            ),
            width=w,
            height=h,
            border_radius="8px",
            overflow="hidden",
            border=f"2px solid var(--{color_scheme}-6)",
        ),
        rx.hstack(
            rx.icon_button(
                rx.icon("undo-2", size=10),
                on_click=rx.call_script(f"window.undoCanvas_{canvas_id}()"),
                size="1", variant="ghost", color_scheme="gray",
                title="Deshacer",
            ),
            rx.icon_button(
                rx.icon("redo-2", size=10),
                on_click=rx.call_script(f"window.redoCanvas_{canvas_id}()"),
                size="1", variant="ghost", color_scheme="gray",
                title="Rehacer",
            ),
            rx.icon_button(
                rx.icon("trash-2", size=10),
                on_click=rx.call_script(f"window.clearCanvas_{canvas_id}()"),
                size="1", variant="ghost", color_scheme="red",
                title="Limpiar",
            ),
            spacing="0",
        ),
        rx.badge(prediction, color_scheme=color_scheme, size="2", variant="soft"),
        align="center", spacing="1",
    )


def _number_group(
    num_id: str, exp_id: str, num_label: str, exp_label: str,
    num_pred: rx.Var[str], exp_pred: rx.Var[str],
) -> rx.Component:
    """Number canvas with exponent as superscript (top-right overlap)."""
    return rx.box(
        # Number (main, centered)
        rx.box(
            _canvas_tile(num_id, num_label, num_pred, "red", "120px", "120px"),
            padding_top="40px",
        ),
        # Exponent (superscript, overlapping top-right)
        rx.box(
            _canvas_tile(exp_id, exp_label, exp_pred, "purple", "50px", "50px"),
            position="absolute",
            top="-20px",
            right="-50px",
        ),
        position="relative",
    )


def _debug_img_tile(label: str, src: rx.Var[str], pred: rx.Var[str]) -> rx.Component:
    """Shows a processed 28x28 debug image with its prediction."""
    return rx.vstack(
        rx.text(label, size="1", color="#888", weight="bold"),
        rx.cond(
            src != "",
            rx.image(
                src=src, width="56px", height="56px",
                style={"image_rendering": "pixelated"},
                border="1px solid #444", border_radius="4px",
            ),
            rx.center(
                rx.text("--", size="1", color="#666"),
                width="56px", height="56px",
                border="1px dashed #444", border_radius="4px",
            ),
        ),
        rx.badge(pred, size="1", variant="outline"),
        align="center", spacing="1",
    )


def _score_bar(
    class_label: rx.Var[str],
    raw_value: rx.Var[str],
    pct_width: rx.Var[str],
    is_top: rx.Var[bool],
) -> rx.Component:
    """One horizontal bar: class label | filled bar | numeric value."""
    return rx.cond(
        raw_value != "",
        rx.hstack(
            rx.text(
                class_label,
                font_size="0.7em",
                color=rx.cond(is_top, "#4ade80", "#666"),
                font_weight="600",
                min_width="16px",
                text_align="right",
            ),
            rx.box(
                rx.box(
                    width=pct_width + "%",
                    height="100%",
                    background=rx.cond(
                        is_top,
                        "linear-gradient(90deg, #22c55e, #4ade80)",
                        "linear-gradient(90deg, #2a2a3e, #3a3a5e)",
                    ),
                    border_radius="3px",
                    transition="width 0.4s ease",
                ),
                width="100%",
                height="14px",
                background="#111118",
                border_radius="3px",
                overflow="hidden",
                flex="1",
            ),
            rx.text(
                raw_value,
                font_size="0.65em",
                font_family="monospace",
                color=rx.cond(is_top, "#4ade80", "#888"),
                min_width="38px",
                text_align="right",
            ),
            spacing="2",
            align_items="center",
            width="100%",
        ),
    )


def _debug_score_card(entry: rx.Var[list[str]]) -> rx.Component:
    """Score card with horizontal confidence bars.

    entry = [label, pred, type, winner_cls, cls0, val0, pct0, cls1, val1, pct1, ...]
    Each class occupies 3 slots starting at index 4. winner_cls (index 3) marks green.
    """
    winner = entry[3]
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.badge(entry[0], size="1", variant="surface", color_scheme="gray"),
                rx.text(entry[1], size="2", weight="bold", color="white"),
                rx.cond(
                    entry[2] != "",
                    rx.badge(entry[2], size="1", variant="outline", color_scheme="blue"),
                ),
                spacing="2", align="center",
            ),
            # Bars — sorted by class ascending, green = winner
            _score_bar(entry[4],  entry[5],  entry[6],  entry[4]  == winner),
            _score_bar(entry[7],  entry[8],  entry[9],  entry[7]  == winner),
            _score_bar(entry[10], entry[11], entry[12], entry[10] == winner),
            _score_bar(entry[13], entry[14], entry[15], entry[13] == winner),
            _score_bar(entry[16], entry[17], entry[18], entry[16] == winner),
            _score_bar(entry[19], entry[20], entry[21], entry[19] == winner),
            _score_bar(entry[22], entry[23], entry[24], entry[22] == winner),
            _score_bar(entry[25], entry[26], entry[27], entry[25] == winner),
            _score_bar(entry[28], entry[29], entry[30], entry[28] == winner),
            _score_bar(entry[31], entry[32], entry[33], entry[31] == winner),
            spacing="1", width="100%",
        ),
        background="#0f0f17",
        border="1px solid #262630",
        border_radius="10px",
        padding="0.75em",
        width="100%",
    )


@rx.page(route="/jugar", title="A Jugar", on_load=ModelState.load_available_models)
def jugar() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            # Main layout: left panel + right content
            rx.flex(
                # Left: control panel or small open button
                rx.cond(
                    GameState.show_panel,
                    # Panel open
                    rx.box(
                        _control_panel(),
                        width=["100%", "100%", "250px"],
                        min_width=["auto", "auto", "250px"],
                    ),
                    # Panel closed: small open button (desktop only)
                    rx.box(
                        rx.icon("panel-left-open", size=18, color="#999"),
                        padding="0.5em",
                        cursor="pointer",
                        border_radius="8px",
                        background="#12121a",
                        border="1px solid #333",
                        _hover={"background": "#1a1a2e", "border_color": "rgba(44, 83, 209, 0.4)"},
                        on_click=GameState.set_show_panel(True),  # type: ignore
                        display=["none", "none", "block"],
                    ),
                ),

                rx.box(
                    rx.vstack(
                        # Canvas grid
                        rx.box(
                            rx.center(
                                rx.flex(
                                    rx.box(_number_group("number_1", "exponent_1", "Num 1", "Exp 1", GameState.pred_number_1, GameState.pred_exponent_1), padding_x="1em"),
                                    rx.box(
                                        _canvas_tile("operator_1", "Op 1", GameState.pred_operator_1, "blue", "80px", "80px"),
                                        align_self="center",
                                        padding_top="40px",
                                        padding_x="1.5em",
                                        margin_left="0.25em",
                                    ),
                                    rx.box(_number_group("number_2", "exponent_2", "Num 2", "Exp 2", GameState.pred_number_2, GameState.pred_exponent_2), padding_x="1em"),
                                    rx.box(
                                        _canvas_tile("operator_2", "Op 2", GameState.pred_operator_2, "blue", "80px", "80px"),
                                        align_self="center",
                                        padding_top="40px",
                                        padding_x="1.5em",
                                        margin_left="0.25em",
                                    ),
                                    rx.box(_number_group("number_3", "exponent_3", "Num 3", "Exp 3", GameState.pred_number_3, GameState.pred_exponent_3), padding_x="1em"),
                                    gap="4",
                                    wrap="wrap",
                                    justify="center",
                                    align="start",
                                ),
                                width="100%",
                                padding="1.5em",
                            ),
                            background="#12121a",
                            border="1px solid #333",
                            border_radius="12px",
                            width="100%",
                        ),
                        # Result + Processed images row
                        rx.cond(
                            GameState.show_debug,
                            rx.flex(

                                rx.cond(
                                    GameState.result != "",
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("calculator", size=14, color="#4ade80"),
                                            rx.text("Resultado", size="2", weight="bold", color="white"),
                                            spacing="2", align_items="center",
                                        ),
                                        rx.box(
                                            rx.hstack(
                                                rx.code(GameState.expression, size="4", weight="bold"),
                                                rx.text("=", size="4", weight="bold", color="#888"),
                                                rx.heading(GameState.result, size="6", weight="bold", color="#4ade80"),
                                                spacing="3", align="center", justify="center", width="100%",
                                            ),
                                            background="rgba(74, 222, 128, 0.05)",
                                            border="1px solid rgba(74, 222, 128, 0.2)",
                                            border_radius="12px",
                                            padding="1em",
                                            width="100%",
                                        ),
                                        spacing="2",
                                        min_width=["100%", "100%", "200px"],
                                        width=["100%", "100%", "auto"],
                                    ),
                                ),

                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("image", size=14, color="#4c8bf5"),
                                        rx.text("Imágenes procesadas (28x28)", size="2", weight="bold", color="white"),
                                        spacing="2", align_items="center",
                                    ),
                                    rx.box(
                                        rx.flex(
                                            _debug_img_tile("Num 1", GameState.debug_img_number_1, GameState.pred_number_1),
                                            _debug_img_tile("Exp 1", GameState.debug_img_exponent_1, GameState.pred_exponent_1),
                                            _debug_img_tile("Op 1", GameState.debug_img_operator_1, GameState.pred_operator_1),
                                            _debug_img_tile("Num 2", GameState.debug_img_number_2, GameState.pred_number_2),
                                            _debug_img_tile("Exp 2", GameState.debug_img_exponent_2, GameState.pred_exponent_2),
                                            _debug_img_tile("Op 2", GameState.debug_img_operator_2, GameState.pred_operator_2),
                                            _debug_img_tile("Num 3", GameState.debug_img_number_3, GameState.pred_number_3),
                                            _debug_img_tile("Exp 3", GameState.debug_img_exponent_3, GameState.pred_exponent_3),
                                            gap="3", wrap="wrap", justify="center",
                                        ),
                                        background="#12121a",
                                        border="1px solid #333",
                                        border_radius="12px",
                                        padding="1em",
                                        width="100%",
                                    ),
                                    spacing="2", flex="1", min_width=["100%", "100%", "0"],
                                ),
                                direction=rx.breakpoints(initial="column", md="row"),
                                gap="2em",
                                width="100%",
                                align_items="stretch",
                            ),
                        ),
                        # Model scores — grouped rows
                        rx.cond(
                            GameState.show_debug & (GameState.debug_entries.length() >= 8),  # type: ignore
                            rx.vstack(
                                # Numbers row
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("hash", size=14, color="#ef4444"),
                                        rx.text("Números", size="2", weight="bold", color="white"),
                                        spacing="2", align_items="center",
                                    ),
                                    rx.el.div(
                                        _debug_score_card(GameState.debug_entries[0]),
                                        _debug_score_card(GameState.debug_entries[1]),
                                        _debug_score_card(GameState.debug_entries[2]),
                                        display="grid",
                                        grid_template_columns=rx.breakpoints(initial="1fr", md="1fr 1fr 1fr"),
                                        gap="0.5em",
                                        width="100%",
                                    ),
                                    spacing="2", width="100%",
                                ),
                                # Exponents row
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("superscript", size=14, color="#a855f7"),
                                        rx.text("Exponentes", size="2", weight="bold", color="white"),
                                        spacing="2", align_items="center",
                                    ),
                                    rx.el.div(
                                        _debug_score_card(GameState.debug_entries[3]),
                                        _debug_score_card(GameState.debug_entries[4]),
                                        _debug_score_card(GameState.debug_entries[5]),
                                        display="grid",
                                        grid_template_columns=rx.breakpoints(initial="1fr", md="1fr 1fr 1fr"),
                                        gap="0.5em",
                                        width="100%",
                                    ),
                                    spacing="2", width="100%",
                                ),
                                # Operators row
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("divide", size=14, color="#3b82f6"),
                                        rx.text("Operadores", size="2", weight="bold", color="white"),
                                        spacing="2", align_items="center",
                                    ),
                                    rx.el.div(
                                        _debug_score_card(GameState.debug_entries[6]),
                                        _debug_score_card(GameState.debug_entries[7]),
                                        display="grid",
                                        grid_template_columns=rx.breakpoints(initial="1fr", md="1fr 1fr"),
                                        gap="0.5em",
                                        width="100%",
                                    ),
                                    spacing="2", width="100%",
                                ),
                                spacing="4", width="100%",
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    flex="1",
                    min_width="0",
                ),
                direction=rx.breakpoints(initial="column", md="row"),
                gap="2em",
                width="100%",
                align_items="flex-start",
                padding=["1em", "1em", "1.5em"],
                max_width="1200px",
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
