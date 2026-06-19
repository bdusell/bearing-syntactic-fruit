import argparse
import enum
import sys

class Number(enum.Enum):
    SINGULAR = enum.auto()
    PLURAL = enum.auto()

NOUNS = [
    ('newt', 'newts'),
    ('orangutan', 'orangutans'),
    ('peacock', 'peacocks'),
    ('quail', 'quails'),
    ('raven', 'ravens'),
    ('salamander', 'salamanders'),
    ('tyrannosaurus', 'tyrannosauruses'),
    ('unicorn', 'unicorns'),
    ('vulture', 'vultures'),
    ('walrus', 'walruses'),
    ('xylophone', 'xylophones'),
    ('yak', 'yaks'),
    ('zebra', 'zebras')
]

NOUN_FORMS = { y for x in NOUNS for y in x }

NOUN_TO_NUMBER = {}
for s_form, p_form in NOUNS:
    NOUN_TO_NUMBER[s_form] = Number.SINGULAR
    NOUN_TO_NUMBER[p_form] = Number.PLURAL

def get_noun_number(noun):
    return NOUN_TO_NUMBER[noun]

class AgreeRecent:

    def __init__(self, verbs: list[tuple[str, str, str]]):
        super().__init__()
        self.past_verb_forms = { x[2] for x in verbs }
        self.past_verb_to_present = {
            Number.SINGULAR : {},
            Number.PLURAL : {}
        }
        for s_form, pl_form, past_form in verbs:
            self.past_verb_to_present[Number.SINGULAR][past_form] = s_form
            self.past_verb_to_present[Number.PLURAL][past_form] = pl_form

    def past_verb_to_present(self, verb, number):
        return self.past_verb_to_present[number][verb]

    def get_agree_recent(self, words):
        match words[-1]:
            case 'PAST':
                return words[:-1]
            case 'PRESENT':
                return list(self.get_agree_recent_present(words[:-1]))
            case _:
                raise ValueError

    def get_agree_recent_present(self, words):
        for word in words:
            if word in NOUN_FORMS:
                last_noun_number = get_noun_number(word)
            elif word in self.past_verb_forms:
                word = self.past_verb_to_present[last_noun_number][word]
            yield word

VERBS = [
    ('giggles', 'giggle', 'giggled'),
    ('smiles', 'smile', 'smiled'),
    ('sleeps', 'sleep', 'slept'),
    ('swims', 'swim', 'swam'),
    ('waits', 'wait', 'waited'),
    ('moves', 'move', 'moved'),
    ('changes', 'change', 'changed'),
    ('reads', 'read', 'read'),
    ('eats', 'eat', 'ate'),
    ('entertains', 'entertain', 'entertained'),
    ('amuses', 'amuse', 'amused'),
    ('high_fives', 'high_five', 'high_fived'),
    ('applauds', 'applaud', 'applauded'),
    ('confuses', 'confuse', 'confused'),
    ('admires', 'admire', 'admired'),
    ('accepts', 'accept', 'accepted'),
    ('remembers', 'remember', 'remembered'),
    ('comforts', 'comfort', 'comforted')
]

DO_VERBS = [
    ('does', 'do', 'did'),
    ("doesn't", "don't", "didn't")
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-do', action='store_true', default=False)
    args = parser.parse_args()
    agree_recent = AgreeRecent(DO_VERBS if args.with_do else VERBS)
    for line in sys.stdin:
        print(' '.join(agree_recent.get_agree_recent(line.split())))

if __name__ == '__main__':
    main()
