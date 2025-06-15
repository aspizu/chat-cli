from typing import cast

from dotenv import load_dotenv
from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Input, Label, Markdown, TextArea

from chat import plugins


class SettingsScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Label("Plugin Path")
        yield Input("google.py", id="plugin_path")
        yield Footer()

    @on(Input.Changed)
    def handle_input_change(self, event: Input.Changed) -> None:
        app = cast(MyApp, self.app)
        if event.input.id == "plugin_path":
            app.plugin_path = event.input.value


class HomeScreen(Screen[None]):
    CSS = """
    #markdown {
        height: 75%
    }
    #textarea {
        height: 25%;
    }
    """

    def compose(self) -> ComposeResult:
        cast(MyApp, self.app)
        yield Markdown("", id="markdown")
        yield TextArea(language="markdown", id="textarea")
        yield Footer()


class MyApp(App[None]):
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        ("ctrl+r", "run", "Run Prompt"),
        ("ctrl+s", "settings", "Toggle Settings"),
    ]

    MODES = {
        "home": HomeScreen,
        "settings": SettingsScreen,
    }

    plugin_path = "google.py"

    def on_mount(self) -> None:
        self.switch_mode("home")

    def action_settings(self) -> None:
        if self.current_mode == "home":
            self.switch_mode("settings")
        else:
            self.switch_mode("home")

    async def action_run(self) -> None:
        markdown = self.screen.query_one("#markdown", Markdown)
        textarea = self.screen.query_one("#textarea", TextArea)
        markdown.set_loading(True)
        output = ""
        try:
            plugin = await plugins.load(self.plugin_path)
            output = await plugin.plugin(textarea.text)
        except Exception as e:
            output = f"```py\n{repr(e)}\n```"
        markdown.set_loading(False)
        markdown.update(output)


load_dotenv()
app = MyApp()
app.run()
