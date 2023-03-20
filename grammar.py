class GrammarRule:
    def __init__(self, left_non_terminal: str, right_part: list[str]):
        self.left_non_terminal = left_non_terminal
        self.right_part = right_part


class Grammar:
    def __init__(self):
        self.alphabet = {}
        self.rules = set()
        self.start = ""
        self.new_start = ""

    def set_alphabet(self, alphabet: dict[str, bool]):
        self.alphabet = alphabet

    def add_rules(self, rules: set[GrammarRule]):
        self.rules |= rules

    def set_start(self, start: str):
        self.start = start

    def set_new_start(self, new_start: str):
        self.new_start = new_start
