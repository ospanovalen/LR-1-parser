from grammar import Grammar, GrammarRule
from situation import Situation
from collections import deque
from copy import deepcopy
from machine_state import MachineState, TableState

END = "$"


class Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = {}
        self.transitions = {}
        self.is_grammar_ok = True
        self.old_start = ""
        self.new_start = ""
        self.table = {}

    def first(self, symbols: list[str]) -> set[str]:
        if len(symbols) == 0 or symbols[0] == END:
            return {END}
        if self.grammar.alphabet[symbols[0]]:
            return {symbols[0]}
        first_symbols = set()
        for rule in self.grammar.rules:
            if rule.left_non_terminal != symbols[0]:
                continue
            if len(rule.right_part) == 0:
                first_symbols |= self.first(symbols[1:])
                continue
            if rule.right_part[0] == rule.left_non_terminal:
                continue
            first_symbols |= self.first(rule.right_part)
        return first_symbols

    def closure(self, situation_set: set[Situation]) -> MachineState:
        has_changed = True
        new_situation_set = deepcopy(situation_set)
        while has_changed:
            has_changed = False
            for situation in new_situation_set:
                if situation.dot_pos == len(situation.right_part):
                    continue
                if self.grammar.alphabet[situation.right_part[situation.dot_pos]]:
                    continue
                for rule in self.grammar.rules:
                    if situation.right_part[situation.dot_pos] != rule.left_non_terminal:
                        continue
                    for non_terminal in self.first(situation.right_part[situation.dot_pos + 1:] + [
                                                                        situation.next_letter]):
                        new_situation = Situation(rule.left_non_terminal, rule.right_part, 0, non_terminal)
                        if new_situation in new_situation_set:
                            continue
                        new_situation_set.add(new_situation)
                        has_changed = True
                if has_changed:
                    break
        return MachineState(new_situation_set)

    def goto(self, state: MachineState, symbol: str) -> MachineState:
        new_situation_set = set()
        for situation in state.situations:
            if situation.dot_pos == len(situation.right_part):
                continue
            if situation.right_part[situation.dot_pos] != symbol:
                continue
            new_situation_set.add(Situation(situation.left_non_terminal, situation.right_part, situation.dot_pos + 1,
                                            situation.next_letter))
        return self.closure(new_situation_set)

    def build_states(self, new_start: str, old_start: str) -> None:
        self.old_start = old_start
        self.new_start = new_start
        start = self.closure({Situation(new_start, [old_start], 0, END)})
        self.states[start] = "q0"
        counter = 1
        visited = set()
        while len(visited) < len(self.states):
            for state in self.states:
                if self.states[state] in visited:
                    continue
                for symbol in self.grammar.alphabet.keys():
                    goto_state = self.goto(state, symbol)
                    if len(goto_state.situations) == 0:
                        continue
                    if goto_state not in self.states:
                        name = "q" + str(counter)
                        self.states[goto_state] = name
                        counter += 1
                    self.transitions.setdefault(self.states[state], {})
                    self.transitions[self.states[state]][symbol] = self.states[goto_state]
                visited.add(self.states[state])
                break

    def build_table(self) -> None:
        for state, name in self.states.items():
            for situation in state.situations:
                if situation.dot_pos == len(situation.right_part):
                    self.table.setdefault(name, {})
                    if situation.left_non_terminal == self.new_start:
                        self.table[name][situation.next_letter] = TableState.get_accept_state()
                    else:
                        self.table[name][situation.next_letter] = TableState.get_reduce_state(
                            GrammarRule(situation.left_non_terminal, situation.right_part))
                else:
                    self.table.setdefault(name, {})
                    for symbol, goto_state in self.transitions[name].items():
                        self.table.setdefault(name, {})
                        self.table[name][symbol] = TableState.get_shift_state(goto_state)

    def parse(self, word: str) -> bool:
        word += END
        word_pos = 0
        path = deque()
        path.append("q0")
        while word_pos < len(word):
            state = path[-1]
            self.table.setdefault(state, {})
            table_pos = self.table[state].get(word[word_pos])
            if table_pos is None:
                return False
            if table_pos.state_type == "a":
                return True
            if table_pos.state_type == "s":
                path.append(word[word_pos])
                path.append(table_pos.goto_state)
                word_pos += 1
            else:
                for i in range(len(table_pos.rule.right_part)):
                    path.pop()
                    path.pop()
                new_state = path[-1]
                path.append(table_pos.rule.left_non_terminal)
                self.table.setdefault(new_state, {})
                new_table_pos = self.table[new_state].get(table_pos.rule.left_non_terminal)
                path.append(new_table_pos.goto_state)
