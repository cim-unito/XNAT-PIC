import flet as ft
from app_modules.modules import AppModules
from route.route_manager import RouteManager


def main(page: ft.Page):
    page.title = "XNAT-PIC ~ XNAT for Preclinical Imaging Centres"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = "CENTER"
    page.vertical_alignment = "START"

    modules = AppModules(page)

    router = RouteManager(page, modules)

    page.on_route_change = router.on_route_change
    page.on_view_pop = router.on_view_pop

    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
