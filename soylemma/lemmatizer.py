from collections import defaultdict
from .utils import installpath
from .utils import VERB, ADJECTIVE, EOMI


class Lemmatizer:
    def __init__(self, verbs=None, adjectives=None,
        eomis=None, lemma_rules=None, dictionary_name='default'):

        verbs, adjectives, eomis = self._check_dictionary(
            verbs, adjectives, eomis, dictionary_name)

        lemma_rules, conjugate_rules = self._check_rules(
            lemma_rules, dictionary_name)

        self.verbs = verbs
        self.adjectives = adjectives
        self.eomis = eomis
        self.lemma_rules = lemma_rules
        self.conjugate_rules = conjugate_rules

    def _check_dictionary(self, verbs, adjectives, eomis, dictionary_name):
        morphs_set = [
            # morphs set, name
            (verbs, 'Verbs'),
            (adjectives, 'Adjectives'),
            (eomis, 'Eomis')
        ]
        morphs_set_ = []
        for morphs, tag in morphs_set:
            if morphs is None:
                morphs = self._load_dictionary(
                    '{}/soylemma/dictionary/{}/{}.txt'.format(
                        installpath, dictionary_name, tag))
            if not isinstance(morphs, set):
                morphs = set(morphs)
            morphs_set_.append(morphs)

        verbs, adjectives, eomis = morphs_set_
        return verbs, adjectives, eomis

    def _load_dictionary(self, path):
        with open(path, encoding='utf-8') as f:
            morphs = {morph.split()[0] for morph in f}
        return morphs

    def _check_rules(self, lemma_rules, dictionary_name):
        if lemma_rules is None:
            lemma_rules = self._load_rules(
                '{}/soylemma/dictionary/{}/rules.txt'.format(
                    installpath, dictionary_name))
        conjugate_rules = self._to_conjugate_rules(lemma_rules)
        return lemma_rules, conjugate_rules

    def _load_rules(self, path):
        with open(path, encoding='utf-8') as f:
            lines = [l.split() for l in f]
        lines = [(l[0], l[1], '아') if len(l) == 2 else l for l in lines]

        # 했던 -> (하, 았던)
        lemma_rules = defaultdict(lambda: set())
        for surf, stem, eomi in lines:
            lemma_rules[surf].add((stem, eomi))
        return dict(lemma_rules)

    def _to_conjugate_rules(self, lemma_rules):
        # (하, 았) -> [했]
        conjugate_rules = defaultdict(lambda: set())
        for surf, canons in lemma_rules.items():
            for stem, eomi in canons:
                conjugate_rules[(stem, eomi)].add(surf)
        return dict(conjugate_rules)

    def analyze(self, word):
        return analyze_morphology(
            word, self.verbs, self.adjectives,
            self.eomis, self.lemma_rules)

    def lemmatize(self, word):
        morphs = analyze_morphology(
            word, self.verbs, self.adjectives,
            self.eomis, self.lemma_rules)
        lemmas = [(stem[0]+'다', stem[1]) for stem, eomi in morphs]
        return lemmas

    def conjugate(self, stem, eomi):
        return get_conjugate_candidates(stem, eomi, self.conjugate_rules)

def analyze_morphology(word, verbs, adjectives, eomis, lemma_rules):
    morphs = []
    for stem, eomi in get_lemma_candidates(word, lemma_rules):
        if not (eomi in eomis):
            continue
        if stem in adjectives:
            morphs.append(((stem, ADJECTIVE), (eomi, EOMI)))
        if stem in verbs:
            morphs.append(((stem, VERB), (eomi, EOMI)))
    return morphs

def get_lemma_candidates(word, rules):
    max_i = len(word) - 1
    candidates = []
    for i, c in enumerate(word):
        l = word[:i+1]
        r = word[i+1:]
        l_ = word[:i]
        if i < max_i:
            candidates.append((l, r))
        # 1 syllable conjugation
        for stem, eomi in rules.get(c, {}):
            for stem, eomi in rules.get(c, {}):
                candidates.append((l_ + stem, eomi + r))
        # 2 or 3 syllables conjugation
        for conj in {word[i:i+2], word[i:i+3]}:
            for stem, eomi in rules.get(conj, {}):
                candidates.append((l_ + stem, eomi + r[1:]))
    return candidates

def get_conjugate_candidates(stem, eomi, rules):
    stem_ = stem[:-1]
    eomi_ = eomi[1:]
    key = (stem[-1], eomi[0])
    candidates = ['{}{}{}'.format(stem_, surface, eomi_) for surface in rules.get(key, {})]
    if len(eomi) >= 2:
        key = (stem[-1], eomi[:2])
        eomi_ = eomi[2:]
        candidates += ['{}{}{}'.format(stem_, surface, eomi_) for surface in rules.get(key, {})]
    candidates.append(stem + eomi)
    return candidates
