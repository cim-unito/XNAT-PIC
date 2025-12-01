from dataclasses import dataclass
from typing import Callable

import flet as ft


@dataclass
class RouteConfig:
    control: ft.Control
    enter_hook: Callable | None = None
    exit_hook: Callable | None = None


class RouteManager:
    def __init__(self, page: ft.Page, modules):
        self.page = page

        self.content_container = ft.Column(expand=True)

        self.page.views.clear()
        self.page.views.append(
            ft.View("/", controls=[self.content_container])
        )

        self.current_route: str | None = None

        self.route_history: list[str] = []

        # ROUTING (declarative setup)
        self.routes: dict[str, RouteConfig] = {
            "/": RouteConfig(control=modules.controls_main),
            "/converter": RouteConfig(control=modules.controls_converter),
            "/uploader": RouteConfig(
                control=modules.controls_uploader,
                enter_hook=modules.controller_uploader.on_enter_route,
                exit_hook=modules.controller_uploader.on_exit_route,
            ),
            "/custom_form": RouteConfig(
                control=modules.controls_custom_form,
                enter_hook=modules.controller_custom_form.on_enter_route,
                exit_hook=modules.controller_custom_form.on_exit_route,
            ),
        }

    def go(self, route: str):
        self.page.go(route)

    def on_route_change(self, e: ft.RouteChangeEvent):
        new_route = e.route

        if self.current_route:
            current_config = self.routes.get(self.current_route)
            if current_config and current_config.exit_hook:
                current_config.exit_hook()
            if self.current_route != new_route:
                self.route_history.append(self.current_route)

        config = self.routes.get(new_route)
        if config is None:
            new_route = "/"
            config = self.routes[new_route]
            self.page.go(new_route)

        self._set_content(config.control)

        if config.enter_hook:
            config.enter_hook()

        self.current_route = new_route

    def on_view_pop(self, e: ft.ViewPopEvent):
        if self.route_history:
            previous_route = self.route_history.pop()
            self.go(previous_route)
        else:
            self.go("/")

    def _set_content(self, control: ft.Control):
        self.content_container.controls = [control]
        self.content_container.update()

