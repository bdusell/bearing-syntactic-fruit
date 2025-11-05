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

PAST_VERB_FORMS = { x[2] for x in VERBS }

PAST_VERB_TO_PRESENT = {
    Number.SINGULAR : {},
    Number.PLURAL : {}
}
for s_form, p_form, past_form in VERBS:
    PAST_VERB_TO_PRESENT[Number.SINGULAR][past_form] = s_form
    PAST_VERB_TO_PRESENT[Number.PLURAL][past_form] = p_form

def past_verb_to_present(verb, number):
    return PAST_VERB_TO_PRESENT[number][verb]

def get_agree_recent(words):
    match words[-1]:
        case 'PAST':
            return words[:-1]
        case 'PRESENT':
            return list(get_agree_recent_present(words[:-1]))
        case _:
            raise ValueError

def get_agree_recent_present(words):
    for word in words:
        if word in NOUN_FORMS:
            last_noun_number = get_noun_number(word)
        elif word in PAST_VERB_FORMS:
            word = past_verb_to_present(word, last_noun_number)
        yield word

def main():
    for line in sys.stdin:
        print(' '.join(get_agree_recent(line.split())))

if __name__ == '__main__':
    main()
