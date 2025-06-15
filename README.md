pluggable chat TUI application.

Add plugins into `./chat/plugins` or write the full absolute path to the plugin file.

Plugin should expose a async plugin function that returns text.

```py
async def plugin(text: str) -> str:
    pass
```
