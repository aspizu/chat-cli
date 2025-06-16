pluggable chat TUI application.

Add plugins into `./chat/plugins` or write the full absolute path to the plugin file.

Plugin should expose a async plugin function that returns text.

```py
async def plugin(text: str) -> str:
    pass
```

## Installation

1. Install uv: <https://docs.astral.sh/uv/getting-started/installation/>

2. Run the following commands:

```shell
uv sync
uv pip install .
```

Run the program from anywhere using `uv run python -m chat`

## Development

```shell
uv sync
uv run python -m chat
```
