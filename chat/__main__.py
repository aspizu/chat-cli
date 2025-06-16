from datetime import datetime
from typing import cast

from dotenv import load_dotenv
from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Input, Label, Markdown, TextArea

from chat import plugins


class SettingsScreen(Screen[None]):
    CSS = """
    Label {
        margin-left: 1;
        margin-top: 1;
        margin-bottom: 1;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        app = cast(MyApp, self.app)
        yield Label("Plugin Path")
        yield Input(app.plugin_path, id="plugin_path")
        yield Label("Plugin Configuration")
        yield Input(app.plugin_config, id="plugin_config")
        yield Footer()

    @on(Input.Changed)
    def handle_input_change(self, event: Input.Changed) -> None:
        app = cast(MyApp, self.app)
        if event.input.id == "plugin_path":
            app.plugin_path = event.input.value
        elif event.input.id == "plugin_config":
            app.plugin_config = event.input.value


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

    plugin_path = "google"
    plugin_config = ""

    def on_mount(self) -> None:
        self.switch_mode("home")
        self.logfile = open("chat_log.txt", "a", encoding="utf-8")

    def action_settings(self) -> None:
        if self.current_mode == "home":
            self.switch_mode("settings")
        else:
            self.switch_mode("home")

    async def action_run(self) -> None:
        markdown = self.screen.query_one("#markdown", Markdown)
        textarea = self.screen.query_one("#textarea", TextArea)
        markdown.set_loading(True)

        # Capture the prompt before processing
        prompt = textarea.text
        timestamp = datetime.now().isoformat()

        output = ""
        try:
            plugin = await plugins.load(self.plugin_path)
            try:
                output = await plugin.plugin(
                    prompt,
                    **plugins.parse_config(self.plugin_config),
                )
            except Exception as e:
                output = (
                    f"```An error occurred while executing plugin:\npy\n{repr(e)}\n```"
                )
        except Exception as e:
            output = f"```An error occurred while loading plugin:\npy\n{repr(e)}\n```"

        markdown.set_loading(False)
        markdown.update(output)

        # Log the interaction in human-readable format
        formatted_timestamp = datetime.fromisoformat(timestamp).strftime(
            "%B %d, %Y at %I:%M:%S %p"
        )
        config_display = " with " + self.plugin_config if self.plugin_config else ""

        log_entry = f"""{"─" * 87}
{formatted_timestamp} using {self.plugin_path}{config_display}

input:
{prompt}

output:
{output}
"""
        self.logfile.write(log_entry)
        self.logfile.flush()


app = MyApp()
try:
    load_dotenv()
    app.run()
finally:
    app.logfile.close()
