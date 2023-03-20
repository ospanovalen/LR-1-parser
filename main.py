from grammar import Grammar, GrammarRule
from parser import Parser


def main():
    alphabet = {}

    print("Enter non-terminals count:")
    non_terminal_count = int(input())

    print("Enter non-terminals:")
    for i in range(non_terminal_count):
        alphabet[input()] = False

    print("Enter terminals count:")
    terminal_count = int(input())

    print("Enter terminals:")
    for i in range(terminal_count):
        alphabet[input()] = True

    grammar = Grammar()
    grammar.set_alphabet(alphabet)

    print("Enter rules count:")
    rule_count = int(input())

    print("A->aB enter like A a B\n"
          "Enter rules:")
    for i in range(rule_count):
        rule = input().split()
        right_part = []
        if len(rule) != 1:
            right_part = rule[1:]
        grammar.add_rules({GrammarRule(rule[0], right_part)})

    print("Enter start non-terminal:")
    start = input()
    grammar.set_start(start)

    print("Enter word:")
    word = input()

    lr = Parser(grammar)
    lr.build_states(start, start)
    lr.build_table()
    print(lr.parse(word))


if __name__ == "__main__":
    main()
