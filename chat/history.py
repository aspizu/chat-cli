from .scrollview import ScrollView


class History(ScrollView):
    def __init__(self) -> None:
        super().__init__(display_line_no=False)
