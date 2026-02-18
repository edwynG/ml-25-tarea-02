import reflex as rx


def footer() -> rx.Component:
    """Footer with credits and links, matching check/ style."""
    return rx.box(
        rx.hstack(
            rx.image(
                src="/favicon.ico",
                width="28px",
                height="28px",
                border_radius="6px",
            ),
            rx.link(
                "Hecho por Fernando Crema García",
                href="https://www.kuleuven.be/wieiswie/en/person/00147342",
                font_size="0.8em",
                color="#666",
                is_external=True,
                _hover={"color": "#aaa"},
            ),
            rx.text("·", color="#444", font_size="0.8em"),
            rx.link(
                "dl.ucv.ai",
                href="https://dl.ucv.ai",
                font_size="0.8em",
                color="#666",
                is_external=True,
                _hover={"color": "#aaa"},
            ),
            rx.text("·", color="#444", font_size="0.8em"),
            rx.link(
                "ml-25.ucv.ai",
                href="https://ml-25.ucv.ai",
                font_size="0.8em",
                color="#666",
                is_external=True,
                _hover={"color": "#aaa"},
            ),
            spacing="3",
            align_items="center",
            justify_content="center",
            wrap="wrap",
        ),
        width="100%",
        padding_y="1.5em",
        border_top="1px solid #333",
        background="linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
    )
