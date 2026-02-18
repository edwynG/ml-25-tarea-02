import reflex as rx

# Import all pages so their @rx.page decorators register routes
import math_recognizer.pages  # noqa: F401

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="blue",
        radius="medium",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    ],
    style={
        "min_height": "100vh",
        "background": "#0a0a0f",
        "font_family": "Inter, sans-serif",
        "::selection": {"background": "var(--accent-a5)"},
    },
)
