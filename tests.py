import pytest

from grammar import Grammar, GrammarRule
from parser import Parser
from situation import Situation
from machine_state import MachineState, TableState


grammar = Grammar()
parser = Parser(Grammar())
old_start = "S"
new_start = "S#"
END = "$"
start_state = MachineState(set())


@pytest.fixture()
def set_grammar():
    grammar.add_rules({GrammarRule(new_start, [old_start]), GrammarRule("S", []),
                       GrammarRule("S", ["S", "a", "S", "b"])})
    grammar.set_start(old_start)
    grammar.set_new_start(new_start)
    grammar.set_alphabet({"S": False, "a": True, "b": True})


def test_first_terminal(set_grammar):
    parser.grammar = grammar
    assert parser.first(["a", "S", "b", "b"]) == {"a"}


def test_first_non_terminal(set_grammar):
    parser.grammar = grammar
    assert parser.first(["S", "a", "S"]) == {"a"}


def test_closure(set_grammar):
    global start_state
    parser.grammar = grammar
    start_state = parser.closure({Situation(new_start, [old_start], 0, END)})
    expected_start = {Situation(new_start, [old_start], 0, END), Situation("S", ["S", "a", "S", "b"], 0, END),
                      Situation("S", [], 0, END), Situation("S", ["S", "a", "S", "b"], 0, "a"),
                      Situation("S", [], 0, "a")}
    assert len(start_state.situations) == len(expected_start)
    for situation in expected_start:
        assert situation in start_state.situations


@pytest.mark.dependency(depends=["test_closure"])
def test_goto():
    expected_goto = {Situation(new_start, [old_start], 1, END), Situation("S", ["S", "a", "S", "b"], 1, END),
                     Situation("S", ["S", "a", "S", "b"], 1, "a")}
    goto_state = parser.goto(start_state, "S")
    assert len(goto_state.situations) == len(expected_goto)
    for situation in expected_goto:
        assert situation in goto_state.situations


def test_build_states():
    parser.build_states(new_start, old_start)

    assert len(parser.states) == 8

    state = MachineState({Situation("S", ["S", "a", "S", "b"], 2, END),
                          Situation("S", ["S", "a", "S", "b"], 2, "a"),
                          Situation("S", ["S", "a", "S", "b"], 0, "b"),
                          Situation("S", [], 0, "b"),
                          Situation("S", ["S", "a", "S", "b"], 0, "a"),
                          Situation("S", [], 0, "a")})
    assert parser.states[state] == "q2"

    state = MachineState({Situation("S", ["S", "a", "S", "b"], 3, END),
                          Situation("S", ["S", "a", "S", "b"], 3, "a"),
                          Situation("S", ["S", "a", "S", "b"], 1, "a"),
                          Situation("S", ["S", "a", "S", "b"], 1, "b")})
    assert parser.states[state] == "q3"

    state = MachineState({Situation("S", ["S", "a", "S", "b"], 2, "b"),
                          Situation("S", ["S", "a", "S", "b"], 2, "a"),
                          Situation("S", ["S", "a", "S", "b"], 0, "b"),
                          Situation("S", ["S", "a", "S", "b"], 0, "a"),
                          Situation("S", [], 0, "b"),
                          Situation("S", [], 0, "a")})
    assert parser.states[state] == "q4"

    state = MachineState({Situation("S", ["S", "a", "S", "b"], 4, END),
                          Situation("S", ["S", "a", "S", "b"], 4, "a")})
    assert parser.states[state] == "q5"

    state = MachineState({Situation("S", ["S", "a", "S", "b"], 3, "b"),
                          Situation("S", ["S", "a", "S", "b"], 3, "a"),
                          Situation("S", ["S", "a", "S", "b"], 1, "b"),
                          Situation("S", ["S", "a", "S", "b"], 1, "a")})
    assert parser.states[state] == "q6"

    state = MachineState({Situation("S", ["S", "a", "S", "b"], 4, "b"),
                          Situation("S", ["S", "a", "S", "b"], 4, "a")})
    assert parser.states[state] == "q7"

    transitions = {"q0": {"S": "q1"}, "q1": {"a": "q2"}, "q2": {"S": "q3"}, "q3": {"a": "q4", "b": "q5"},
                   "q4": {"S": "q6"}, "q6": {"a": "q4", "b": "q7"}}

    assert transitions == parser.transitions


@pytest.mark.dependency(depends=["test_build_states"])
def test_build_table():
    parser.build_table()
    second_rule = GrammarRule("S", ['S', "a", "S", "b"])
    first_rule = GrammarRule(new_start, [old_start])
    expected_table = {
     "q0": {"S": TableState.get_shift_state("q1"),
            "a": TableState.get_reduce_state(second_rule),
            "$": TableState.get_reduce_state(second_rule)},
     "q1": {"a": TableState.get_shift_state("q2"),
            "$": TableState.get_accept_state()},
     "q2": {"S": TableState.get_shift_state("q3"),
            "b": TableState.get_reduce_state(second_rule),
            "a": TableState.get_reduce_state(second_rule)},
     "q3": {"a": TableState.get_shift_state("q4"),
            "b": TableState.get_shift_state("q5")},
     "q4": {"S": TableState.get_shift_state("q6"),
            "b": TableState.get_reduce_state(second_rule),
            "a": TableState.get_reduce_state(second_rule)},
     "q5": {"$": TableState.get_reduce_state(first_rule),
            "a": TableState.get_reduce_state(first_rule)},
     "q6": {"a": TableState.get_shift_state("q4"),
            "b": TableState.get_shift_state("q7")},
     "q7": {"b": TableState.get_reduce_state(first_rule),
            "a": TableState.get_reduce_state(first_rule)}}

    for state, transitions in parser.table.items():
        for symbol, transition in transitions.items():
            assert expected_table[state][symbol].state_type == transition.state_type


test_grammar = Grammar()
test_grammar.add_rules({GrammarRule("S", []), GrammarRule("S", ["a", "S", "b", "S"])})
test_grammar.set_start(old_start)
test_grammar.set_alphabet({"S": False, "a": True, "b": True})
test_parser = Parser(test_grammar)
test_parser.build_states(new_start, old_start)
test_parser.build_table()


def test_1():
    assert test_parser.parse("abab") is True


def test_2():
    assert test_parser.parse("aabb") is True


def test_3():
    assert test_parser.parse("bbb") is False


def test_4():
    assert test_parser.parse("aaaabbbabb") is True


def test_5():
    assert test_parser.parse("aaaaabbbbbabaabbabaabbb") is False
