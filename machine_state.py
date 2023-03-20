from situation import Situation
from grammar import GrammarRule

hash_mod = 10_000_000_007


class MachineState:
    def __init__(self, situations: set[Situation]):
        self.situations = situations

    def __eq__(self, other):
        return tuple(sorted(self.situations)) == tuple(sorted(other.situations))

    def __hash__(self):
        situation_hash = 0
        mod = int(hash_mod ** len(self.situations))
        for situation in sorted(self.situations):
            situation_hash ^= int(hash(situation) * mod)
            mod /= hash_mod
        return situation_hash


class TableState:
    def __init__(self):
        self.state_type = None
        self.rule = None
        self.goto_state = None

    def set_type(self, state_type: str) -> None:
        self.state_type = state_type

    def set_rule(self, rule: GrammarRule) -> None:
        self.rule = rule

    def set_goto_state(self, goto_state: str) -> None:
        self.goto_state = goto_state

    @staticmethod
    def get_shift_state(goto_state: str):
        state = TableState()
        state.state_type = "s"
        state.goto_state = goto_state
        return state

    @staticmethod
    def get_reduce_state(rule: GrammarRule):
        state = TableState()
        state.state_type = "r"
        state.rule = rule
        return state

    @staticmethod
    def get_accept_state():
        state = TableState()
        state.state_type = "a"
        return state
