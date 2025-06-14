import textwrap

from . import terminal as t


def wrap_preserve_newlines(text: str, width: int):
    lines = text.splitlines()  # Split at actual newlines
    wrapped_lines: list[str] = []
    for line in lines:
        if line.strip():  # Non-empty line
            wrapped = textwrap.wrap(line, width=width)
            wrapped_lines.extend(wrapped)
        else:
            # Preserve blank lines
            wrapped_lines.append("")
    return wrapped_lines


class ScrollView:
    def __init__(self, display_line_no: bool = False) -> None:
        self.lines: list[str] = []
        self.scroll: int = 0
        self.line: int = 0
        self.height: int = 0
        self.display_line_no = display_line_no

    def render(self, y: int, height: int) -> None:
        self.height = height
        self.handle_scroll()
        t.m(0, y)
        for i in range(height):
            line = ""
            t.w(t.brblack)
            if self.scroll + i < len(self.lines):
                if self.display_line_no:
                    t.w(f"{self.scroll + i + 1:>4}{t.black}│")
                line = self.lines[self.scroll + i]
            elif self.display_line_no:
                t.w(" " * 4 + "│")
            t.w(t.reset)
            t.w(line)
            if len(self.lines) > height:
                t.w(" " * (t.width - (6 if self.display_line_no else 1) - len(line)))
                scrollbar_height = 4
                max_scroll = len(self.lines) - height
                if max_scroll > 0:
                    if self.scroll >= max_scroll:
                        scrollbar_top = height - scrollbar_height
                    else:
                        factor = self.scroll / max_scroll
                        scrollbar_top = min(
                            height - scrollbar_height,
                            round(factor * (height - scrollbar_height)),
                        )
                else:
                    scrollbar_top = 0
                if (i >= scrollbar_top) and (i < scrollbar_top + scrollbar_height):
                    t.w(t.bgwhite)
                else:
                    t.w(t.brbgblack)
                t.w(f" {t.reset}")
            if i != height - 1:
                t.w("\n")

    def handle_scroll(self) -> None:
        if self.line - self.scroll < 0:
            self.scroll = self.line
        if self.line - self.scroll > max(0, self.height - 1):
            self.scroll += (self.line - self.scroll) - (self.height - 1)

    def handle_key(self, key: str) -> None:
        match key:
            case "UP_ARROW":
                self.line = max(0, self.line - 1)
            case "DOWN_ARROW":
                self.line = min(self.line + 1, len(self.lines) - 1)
            case _:
                pass

    def append_content(self, content: str) -> None:
        self.lines.extend(
            wrap_preserve_newlines(
                content, t.width - (6 if self.display_line_no else 1)
            )
        )

    def get_text(self) -> str:
        return "\n".join(self.lines)
