import argparse
import collections
import dataclasses
import enum
import sys

class Number(enum.Enum):
    SINGULAR = enum.auto()
    PLURAL = enum.auto()

@dataclasses.dataclass
class MoveSecond:
    determiners: set[str]
    prepositions: set[str]
    verbs: set[str]

    def __call__(self, words):
        match words[-1]:
            case 'decl':
                return words[:-1]
            case 'passiv':
                subject_noun_phrase = words[:2]
                for i in range(2, len(words)):
                    if words[i] in self.determiners:
                        if words[i+2] in self.prepositions:
                            m = 5
                        else:
                            m = 2
                        object_noun_phrase = words[i:i+m]
                        break
                else:
                    raise ValueError('second noun phrase is missing')
                for i in range(2, len(words)):
                    if words[i] in self.verbs:
                        verb = words[i]
                        break
                else:
                    raise ValueError('verb is missing')
                return self.to_passive(subject_noun_phrase, verb, object_noun_phrase)
            case _:
                raise ValueError

    def to_passive(self, subject_noun_phrase, verb, object_noun_phrase):
        raise NotImplementedError

class EnglishMoveSecond(MoveSecond):

    def __init__(self):
        # See https://github.com/sebschu/multilingual-transformations/blob/e848833f2df7674022ef02e2b649482d23ade7a7/data/passiv_en_nps/passivization.gr
        super().__init__(
            determiners={
                'the',
                'some',
                'my',
                'your',
                'our',
                'her'
            },
            prepositions={
                'around',
                'near',
                'with',
                'upon',
                'by',
                'behind',
                'above',
                'below'
            },
            verbs={
                'entertained',
                'amused',
                'annoyed',
                'applauded',
                'confused',
                'admired',
                'accepted',
                'remembered',
                'comforted'
            },
        )
        self.singular_nouns = {
            'newt',
            'orangutan',
            'peacock',
            'quail',
            'raven',
            'salamander',
            'tyrannosaurus',
            'unicorn',
            'vulture',
            'walrus',
            'xylophone',
            'yak',
            'zebra'
        }

    def to_passive(self, subject_noun_phrase, verb, object_noun_phrase):
        return [
            *object_noun_phrase,
            self.inflect_was(self.number_of_noun_phrase(object_noun_phrase)),
            verb,
            'by',
            *subject_noun_phrase,
            '.'
        ]

    def inflect_was(self, number):
        match number:
            case Number.SINGULAR:
                return 'was'
            case Number.PLURAL:
                return 'were'
            case _:
                raise ValueError

    def number_of_noun_phrase(self, noun_phrase):
        if noun_phrase[1] in self.singular_nouns:
            return Number.SINGULAR
        else:
            return Number.PLURAL

class GermanMoveSecond(MoveSecond):

    def __init__(self):
        # See https://github.com/sebschu/multilingual-transformations/blob/e848833f2df7674022ef02e2b649482d23ade7a7/data/passiv_de_nps/passiv_de_nps.gr
        # and https://github.com/sebschu/multilingual-transformations/blob/e848833f2df7674022ef02e2b649482d23ade7a7/data/passiv_de_nps/passivization_corpus_proc.py#L138C1-L158C1
        determiners = [
            # nom s, acc s, dat s, nom/acc pl, dat pl
            ('der', 'den', 'dem', 'die', 'den'),
            ('ein', 'einen', 'einem', 'einige', 'einigen'),
            ('mein', 'meinen', 'meinem', 'meine', 'meinen'),
            ('dein', 'deinen', 'deinem', 'deine', 'deinen'),
            ('unser', 'unseren', 'unserem', 'unsere', 'unseren'),
            ('ihr', 'ihren', 'ihrem', 'ihre', 'ihren')
        ]
        self.determiner_nom_numbers = index_nom_numbers(determiners)
        self.determiner_acc_or_dat_numbers = index_acc_or_dat_numbers(determiners)
        self.determiner_to_nom = index_to_nom(determiners)
        self.determiner_to_dat = index_to_dat(determiners)
        nouns = [
            # nom s, acc s, dat s, nom/acc pl, dat pl
            ('Molch', 'Molch', 'Molch', 'Molche', 'Molchen'),
            ('Löwe', 'Löwen', 'Löwen', 'Löwen', 'Löwen'),
            ('Pfau', 'Pfau', 'Pfau', 'Pfaue', 'Pfauen'),
            ('Kater', 'Kater', 'Kater', 'Kater', 'Katern'),
            ('Rabe', 'Raben', 'Raben', 'Raben', 'Raben'),
            ('Salamander', 'Salamander', 'Salamander', 'Salamander', 'Salamandern'),
            ('Dinosaurier', 'Dinosaurier', 'Dinosaurier', 'Dinosaurier', 'Dinosauriern'),
            ('Papagei', 'Papagei', 'Papagei', 'Papageie', 'Papageien'),
            ('Geier', 'Geier', 'Geier', 'Geier', 'Geiern'),
            ('Wellensittich', 'Wellensittich', 'Wellensittich', 'Wellensittiche', 'Wellensittichen'),
            ('Esel', 'Esel', 'Esel', 'Esel', 'Eseln'),
            ('Hund', 'Hund', 'Hund', 'Hunde', 'Hunden'),
            ('Ziesel', 'Ziesel', 'Ziesel', 'Ziesel', 'Zieseln')
        ]
        self.noun_nom_numbers = index_nom_numbers(nouns)
        self.noun_acc_or_dat_numbers = index_acc_or_dat_numbers(nouns)
        self.noun_to_nom = index_to_nom(nouns)
        self.noun_to_dat = index_to_dat(nouns)
        verbs = [
            # past 3 sg, past 3 pl, passive participle
            ('unterhielt', 'unterhielten', 'unterhalten'),
            ('amüsierte', 'amüsierten', 'amüsiert'),
            ('nervte', 'nervten', 'genervt'),
            ('erfreute', 'erfreuten', 'erfreut'),
            ('verwirrte', 'verwirrten', 'verwirrt'),
            ('bewunderte', 'bewunderten', 'bewundert'),
            ('akzeptierte', 'akzeptierten', 'akzeptiert'),
            ('bedauerte', 'bedauerten', 'bedauert'),
            ('tröstete', 'trösteten', 'getröstet')
        ]
        self.verb_to_participle = {}
        for sg, pl, part in verbs:
            self.verb_to_participle[sg] = part
            self.verb_to_participle[pl] = part
        super().__init__(
            # Just include the acc and dat forms.
            determiners={ y for x in determiners for y in x[1:] },
            prepositions={
                'bei',
                'neben',
                'hinter',
                'über',
                'unter'
            },
            # Just include the past 3 sg and pl forms.
            verbs={y for x in verbs for y in x[:2]}
        )

    def to_passive(self, subject_noun_phrase, verb, object_noun_phrase):
        number = self.number_of_acc_or_dat_noun_phrase(object_noun_phrase)
        return [
            *self.noun_phrase_acc_or_dat_to_nom(object_noun_phrase, number),
            self.inflect_wurde(number),
            'von',
            *self.noun_phrase_nom_to_dat(subject_noun_phrase),
            self.verb_to_participle[verb],
            '.'
        ]

    def number_of_nom_noun_phrase(self, noun_phrase):
        number, = self.determiner_nom_numbers[noun_phrase[0]] & self.noun_nom_numbers[noun_phrase[1]]
        return number

    def number_of_acc_or_dat_noun_phrase(self, noun_phrase):
        numbers = self.determiner_acc_or_dat_numbers[noun_phrase[0]] & self.noun_acc_or_dat_numbers[noun_phrase[1]]
        # If the number is ambiguous, assume singular.
        if len(numbers) > 1:
            return Number.SINGULAR
        else:
            number, = numbers
            return number

    def noun_phrase_acc_or_dat_to_nom(self, noun_phrase, number):
        return [
            self.determiner_to_nom[noun_phrase[0], number],
            self.noun_to_nom[noun_phrase[1], number],
            *noun_phrase[2:]
        ]

    def noun_phrase_nom_to_dat(self, noun_phrase):
        if len(noun_phrase) != 2:
            raise ValueError
        number = self.number_of_nom_noun_phrase(noun_phrase)
        return [
            self.determiner_to_dat[noun_phrase[0], number],
            self.noun_to_dat[noun_phrase[1], number]
        ]

    def inflect_wurde(self, number):
        match number:
            case Number.SINGULAR:
                return 'wurde'
            case Number.PLURAL:
                return 'wurden'
            case _:
                raise ValueError

def index_nom_numbers(lexemes):
    result = collections.defaultdict(set)
    for nom_s, acc_s, dat_s, nom_acc_pl, dat_pl in lexemes:
        result[nom_s].add(Number.SINGULAR)
        result[nom_acc_pl].add(Number.PLURAL)
    return dict(result.items())

def index_acc_or_dat_numbers(lexemes):
    result = collections.defaultdict(set)
    for nom_s, acc_s, dat_s, nom_acc_pl, dat_pl in lexemes:
        for form in (acc_s, dat_s):
            result[form].add(Number.SINGULAR)
        for form in (nom_acc_pl, dat_pl):
            result[form].add(Number.PLURAL)
    return dict(result.items())

def index_to_nom(lexemes):
    result = {}
    for nom_s, acc_s, dat_s, nom_acc_pl, dat_pl in lexemes:
        for form in (acc_s, dat_s):
            result[form, Number.SINGULAR] = nom_s
        for form in (nom_acc_pl, dat_pl):
            result[form, Number.PLURAL] = nom_acc_pl
    return result

def index_to_dat(lexemes):
    result = {}
    for nom_s, acc_s, dat_s, nom_acc_pl, dat_pl in lexemes:
        result[nom_s, Number.SINGULAR] = dat_s
        result[nom_acc_pl, Number.PLURAL] = dat_pl
    return result

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--language', choices=['en', 'de'], required=True)
    args = parser.parse_args()

    match args.language:
        case 'en':
            rule = EnglishMoveSecond()
        case 'de':
            rule = GermanMoveSecond()
        case _:
            raise ValueError

    for line in sys.stdin:
        print(' '.join(rule(line.split())))

if __name__ == '__main__':
    main()
