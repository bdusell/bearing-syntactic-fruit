import sys

AUXILIARY_VERBS = { 'do', 'does', 'don\'t', 'doesn\'t' }

def get_move_first(words):
    match words[-1]:
        case 'decl':
            return words[:-1]
        case 'quest':
            assert words[-2] == '.'
            for i, word in enumerate(words):
                if word in AUXILIARY_VERBS:
                    break
            else:
                raise ValueError
            return [words[i], *words[:i], *words[i+1:-2], '?']
        case _:
            raise ValueError

def main():
    for line in sys.stdin:
        print(' '.join(get_move_first(line.split())))

if __name__ == '__main__':
    main()
