class Situation:
    def __init__(self, left_non_terminal: str, right_part: list, dot_pos: int, next_letter: str):
        self.left_non_terminal = left_non_terminal
        self.right_part = right_part
        self.dot_pos = dot_pos
        self.next_letter = next_letter

    def __eq__(self, other):
        return (self.next_letter == other.next_letter) and (self.dot_pos == other.dot_pos) and (
                self.left_non_terminal.__eq__(other.left_non_terminal)) and (
                self.right_part.__eq__(other.right_part))

    def __lt__(self, other):
        return (self.left_non_terminal, tuple(self.right_part), self.dot_pos, self.next_letter) < \
               (other.left_non_terminal, tuple(other.right_part), other.dot_pos, other.next_letter)

    def __hash__(self):
        situation_hash = hash(self.left_non_terminal) ^ hash(self.dot_pos) ^ hash(self.next_letter)
        for symbol in self.right_part:
            situation_hash = situation_hash ^ hash(symbol)
        return situation_hash
