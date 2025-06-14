from . import terminal as t
from .scrollview import ScrollView


class Editor(ScrollView):
    def __init__(self) -> None:
        super().__init__(display_line_no=True)
        self.lines.append("")
        self.column: int = 0

    def render(self, y: int, height: int) -> None:
        super().render(y, height)
        t.m(5 + self.column, y + self.line - self.scroll)

    def handle_key(self, key: str) -> None:
        match key:
            case "RIGHT_ARROW":
                self.column = min(len(self.lines[self.line]), self.column + 1)
            case "LEFT_ARROW":
                self.column = max(0, self.column - 1)
            case "UP_ARROW":
                self.line = max(0, self.line - 1)
                self.column = min(self.column, len(self.lines[self.line]))
            case "DOWN_ARROW":
                self.line = min(self.line + 1, len(self.lines) - 1)
                self.column = min(self.column, len(self.lines[self.line]))
            case "HOME":
                self.column = 0
            case "END":
                self.column = len(self.lines[self.line])
            case "\n":
                line = self.lines[self.line]
                self.lines.insert(self.line + 1, line[self.column :])
                self.lines[self.line] = line[: self.column]
                self.line += 1
                self.column = 0
            case "BACKSPACE":
                line = self.lines[self.line]
                if self.column == 0:
                    if self.line == 0:
                        return
                    previous_line_length = len(self.lines[self.line - 1])
                    self.lines[self.line - 1] += line
                    del self.lines[self.line]
                    self.line -= 1
                    self.column = previous_line_length
                    self.scroll = max(0, self.scroll - 1)
                    return
                self.lines[self.line] = line[: self.column - 1] + line[self.column :]
                self.column -= 1
            case ch if len(ch) == 1:
                line = self.lines[self.line]
                self.lines[self.line] = line[: self.column] + ch + line[self.column :]
                self.column += 1
            case _:
                pass

    def clear(self) -> None:
        self.lines = [""]
        self.line = 0
        self.column = 0
        self.scroll = 0
