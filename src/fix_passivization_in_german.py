import sys

def fix_line(line):
    source_str, target_str = line.split('\t', 1)
    source = source_str.split()
    target = target_str.split()
    match source[-1]:
        case 'passiv':
            return f'{source_str}\t{" ".join(fix_passive(target))}'
        case 'decl':
            return line
        case _:
            raise ValueError

SINGULAR_DETERMINERS = {
    'der',
    'ein',
    'mein',
    'dein',
    'unser',
    'ihr'
}

def fix_passive(words):
    words = list(words)
    if words[0] in SINGULAR_DETERMINERS:
        match words[1]:
            case 'Löwen':
                words[1] = 'Löwe'
            case 'Raben':
                words[1] = 'Rabe'
    return words

def main():
    for line in sys.stdin:
        print(fix_line(line.rstrip('\n')))

if __name__ == '__main__':
    main()
