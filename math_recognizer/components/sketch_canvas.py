import reflex as rx


class SketchCanvas(rx.NoSSRComponent):
    """Wrapper around react-sketch-canvas with global export/clear functions."""

    library = "$/public/sketch_canvas_component.jsx"
    tag = "SketchCanvasWrapper"
    is_default = True

    lib_dependencies: list[str] = ["react-sketch-canvas@6.2.0"]

    # Props passed to the JS component (Reflex auto-converts snake_case to camelCase)
    canvas_id: rx.Var[str]
    width: rx.Var[str]
    height: rx.Var[str]
    stroke_width: rx.Var[int]
    stroke_color: rx.Var[str]
    canvas_color: rx.Var[str]


sketch_canvas = SketchCanvas.create
