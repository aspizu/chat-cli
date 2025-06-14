import asyncio
import importlib.util
import os
import pathlib
import shlex
from math import floor
from typing import Any, Protocol, cast

from . import terminal as t
from .editor import Editor
from .history import History


class PluginProtocol(Protocol):
    async def plugin(self, input: str) -> str:
        raise NotImplementedError


class App:
    def __init__(self) -> None:
        self.history = History()
        self.editor = Editor()
        self.editor_focused: bool = True
        self.plugin = "google.py"
        self.plugin_module: PluginProtocol | None = None
        self.load_plugin(self.plugin)
        self.loading: bool = False
        self.params: dict[str, Any] = {}

    def render(self) -> None:
        t.c()
        t.h()
        msg = (
            "Loading..."
            if self.loading
            else "Press TAB to switch between editor and history"
        )
        t.w(
            t.brblack
            + msg
            + ("─" if self.editor_focused else "━") * (t.width - len(msg))
            + "\n"
        )
        y = 1
        self.history.render(y, floor(t.height * 0.75) - 2)
        y = floor(t.height * 0.75)
        t.m(0, y)
        t.w(t.brblack + ("━" if self.editor_focused else "─") * t.width + "\n")
        y += 1
        self.editor.render(y, t.height - y)
        t.f()

    async def handle_key(self, key: str) -> None:
        if key == "TAB":
            self.editor_focused = not self.editor_focused
        if self.editor_focused:
            self.editor.handle_key(key)
            if key == "CTRL_R":
                await self.handle_execute()
                return
        else:
            self.history.handle_key(key)

    async def run(self) -> None:
        t.setmode()

        try:
            while True:
                self.render()
                key = t.read()
                await self.handle_key(key)

        finally:
            t.chf()
            t.resetmode()

    async def handle_execute(self) -> None:
        input = self.editor.get_text()
        if input.startswith("/"):
            output = self.handle_command(input.removeprefix("/"))
            if output is not None:
                self.history.append_content(output)
            return
        asyncio.create_task(self.execute_plugin(input))
        self.loading = True
        while self.loading:
            self.render()
            await asyncio.sleep(0.1)

    def handle_command(self, command: str) -> str | None:
        self.editor.clear()
        parts = shlex.split(command)
        if len(parts) == 1:
            if parts[0] == "clear" or parts[0] == "cls":
                self.history.lines.clear()
                return None
            elif parts[0] == "exit":
                raise KeyboardInterrupt
        if len(parts) == 2:
            if parts[0] == "plugin":
                try:
                    self.load_plugin(parts[1])
                except ImportError as e:
                    return str(e)

    def load_plugin(self, path: str) -> None:
        if not pathlib.Path(path).is_absolute():
            path = os.path.join(os.path.dirname(__file__), "plugins", path)

        module_name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load plugin from {path}")
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except FileNotFoundError as e:
            raise ImportError(f"Plugin file not found: {e.filename}") from e
        self.plugin = path
        self.plugin_module = cast(Any, module)

    async def execute_plugin(self, input: str) -> None:
        if not self.plugin_module:
            self.history.append_content("No plugin loaded.")
            self.loading = False
            return
        output = await self.plugin_module.plugin(input)
        self.history.append_content(output)
        self.loading = False
