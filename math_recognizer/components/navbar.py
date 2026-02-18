import reflex as rx


class NavState(rx.State):
    """State for mobile menu toggle and route tracking."""
    mobile_menu_open: bool = False

    @rx.var
    def current_path(self) -> str:
        return self.router.url.path

    def toggle_mobile_menu(self):
        self.mobile_menu_open = not self.mobile_menu_open

    def close_mobile_menu(self):
        self.mobile_menu_open = False


# Navigation items: (label, href, icon)
_NAV_ITEMS = [
    ("Inicio", "/", "home"),
    ("A Jugar", "/jugar", "gamepad-2"),
    ("Generador", "/generar-datos", "brush"),
    ("MNIST", "/canvas-demo", "database"),
    ("Modelos", "/cargar-modelos", "upload"),
]


def _nav_item(label: str, href: str, icon: str) -> rx.Component:
    """Desktop nav item with active route highlight."""
    active = NavState.current_path == href
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=14),
            rx.text(label, font_size="0.85em", font_weight="600"),
            spacing="2",
            align_items="center",
        ),
        href=href,
        padding_x="1em",
        padding_y="0.5em",
        border_radius="8px",
        color=rx.cond(active, "white", "#999"),
        background=rx.cond(active, "rgba(44, 83, 209, 0.25)", "transparent"),
        border=rx.cond(active, "1px solid rgba(44, 83, 209, 0.4)", "1px solid transparent"),
        _hover={"background": "rgba(44, 83, 209, 0.2)", "color": "white"},
        transition="all 0.2s ease",
        text_decoration="none",
    )


def _mobile_nav_item(label: str, href: str, icon: str) -> rx.Component:
    """Mobile nav item."""
    active = NavState.current_path == href
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=16),
            rx.text(label, font_size="0.9em", font_weight="600"),
            spacing="2",
            align_items="center",
        ),
        href=href,
        padding_x="1em",
        padding_y="0.75em",
        border_radius="8px",
        color=rx.cond(active, "#93b4ff", "#999"),
        background=rx.cond(active, "rgba(44, 83, 209, 0.2)", "transparent"),
        _hover={"background": "rgba(255, 255, 255, 0.05)"},
        transition="all 0.2s ease",
        width="100%",
        text_decoration="none",
        on_click=NavState.close_mobile_menu,
    )


def navbar() -> rx.Component:
    """Sticky header with navy gradient, favicon, nav items, mobile hamburger."""
    return rx.box(
        # Main bar
        rx.box(
            rx.hstack(
                # Logo + title
                rx.link(
                    rx.hstack(
                        rx.image(
                            src="/favicon.ico",
                            width="42px",
                            height="42px",
                            border_radius="8px",
                        ),
                        rx.vstack(
                            rx.text(
                                "Dígitos",
                                font_size="1.2em",
                                font_weight="800",
                                color="white",
                                letter_spacing="-0.02em",
                                line_height="1.2",
                            ),
                            rx.text(
                                "Escuela de Computación",
                                font_size="0.7em",
                                color="#888",
                                letter_spacing="0.05em",
                            ),
                            rx.text(
                                "Universidad Central de Venezuela",
                                font_size="0.7em",
                                color="#888",
                                letter_spacing="0.05em",
                            ),
                            spacing="0",
                            align_items="flex-start",
                        ),
                        spacing="3",
                        align_items="center",
                    ),
                    href="/",
                    text_decoration="none",
                    _hover={"opacity": "0.9"},
                ),
                # Desktop nav
                rx.hstack(
                    *[_nav_item(label, href, icon) for label, href, icon in _NAV_ITEMS],
                    spacing="1",
                    align_items="center",
                    display=["none", "none", "flex"],
                ),
                # Badge + hamburger
                rx.hstack(
                    rx.badge(
                        "Tarea 2",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                    ),
                    # Hamburger (mobile only)
                    rx.box(
                        rx.cond(
                            NavState.mobile_menu_open,
                            rx.icon("x", size=24, color="#999"),
                            rx.icon("menu", size=24, color="#999"),
                        ),
                        padding="0.4em",
                        cursor="pointer",
                        border_radius="6px",
                        _hover={"background": "rgba(255, 255, 255, 0.05)"},
                        on_click=NavState.toggle_mobile_menu,
                        display=["block", "block", "none"],
                    ),
                    spacing="3",
                    align_items="center",
                ),
                width="100%",
                max_width="1100px",
                margin_x="auto",
                padding_x="1em",
                padding_y="0.75em",
                align_items="center",
                justify_content="space-between",
            ),
        ),
        # Mobile dropdown menu
        rx.cond(
            NavState.mobile_menu_open,
            rx.box(
                rx.vstack(
                    *[_mobile_nav_item(label, href, icon) for label, href, icon in _NAV_ITEMS],
                    spacing="1",
                    width="100%",
                    padding="1em",
                ),
                border_top="1px solid #333",
                background="#12121a",
                display=["block", "block", "none"],
            ),
        ),
        position="sticky",
        top="0",
        z_index="50",
        background="linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
        border_bottom="1px solid #333",
        width="100%",
    )
