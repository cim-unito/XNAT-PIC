import flet as ft


class RouteManager:
    def __init__(self, page: ft.Page, modules):
        self.page = page
        self.modules = modules

        self.content_container = ft.Column(expand=True)

        self.page.views.clear()
        self.page.views.append(
            ft.View("/", controls=[self.content_container])
        )

        self.current_route: str | None = None

        # ROUTING
        self.routes = {
            "/": modules.controls_main,
            "/converter": modules.controls_converter,
            "/uploader": modules.controls_uploader,
        }

        self.enter_hooks = {
            "/uploader": modules.controller_uploader.on_enter_route,
        }
        self.exit_hooks = {
            "/uploader": modules.controller_uploader.on_exit_route,
        }

    def go(self, route: str):
        self.page.go(route)

    def on_route_change(self, e: ft.RouteChangeEvent):

        new_route = self.page.route

        if self.current_route:
            hook_exit = self.exit_hooks.get(self.current_route)
            if hook_exit:
                hook_exit()

        controls = self.routes.get(new_route)
        if controls is None:
            new_route = "/"
            controls = self.routes["/"]
            self.page.go("/")

        self._set_content(controls)

        hook_enter = self.enter_hooks.get(new_route)
        if hook_enter:
            hook_enter()

        self.current_route = new_route

    def on_view_pop(self, e: ft.ViewPopEvent):
        self.go("/")

    def _set_content(self, controls):
        self.content_container.controls = [controls]
        self.content_container.update()
