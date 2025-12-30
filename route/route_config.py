from dataclasses import dataclass
from typing import Callable

import flet as ft


@dataclass
class RouteConfig:
    control: ft.Control
    enter_hook: Callable | None = None
    exit_hook: Callable | None = None
