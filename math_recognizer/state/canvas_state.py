import reflex as rx


class CanvasState(rx.State):
    """State for canvas drawing configuration."""

    stroke_width: int = 3
    stroke_color: str = "#ffffff"
    canvas_bg_color: str = "#333333"

    def update_stroke_width(self, value: list[float]):
        self.stroke_width = int(value[0])
