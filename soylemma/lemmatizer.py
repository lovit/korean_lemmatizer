from collections import defaultdict
from .utils import installpath
from .utils import VERB, ADJECTIVE, EOMI


class Lemmatizer:
    """
    Korean trained lemmatizer class

    Arguments
    ---------
    verbs, adjectives, eomis : set of str
        Dictionary set
        If they are None, use trained dictionary.
    lemma_rules : dict
        Dictionary of lemmatization rules.
        For example,
            lemma_rules = {
                '했': {('하', '았')},
                '끔': {('끈', 'ㅁ'), ('끌', 'ㅁ')}
                '가우니': {('갑', '니')} # 차가우니까 -> 차갑 + 니까
                ...
            }
    dictionary_name : str
        Dictionary name.
        User can use their dictionary
        Dictionary file path is soylemma/dictionary/[dictionary_name]/
        Each dictionary must have four files
            |-- Adjectives.txt
            |-- Eomis.txt
            |-- Verbs.txt
            |-- rules.txt

    Usage
    -----

        >>> from soylemma import Lemmatizer

        >>> lemmatizer = Lemmatizer(dictionary_name='demo')
        >>> lemmatizer = Lemmatizer(dictionary_name='default')

        >>> lemmatizer.lemmatize('차가우니까')
        $ [('차갑다', 'Adjective')]

        >>> lemmatizer.analyze('차가우니까')
        $ [(('차갑', 'Adjective'), ('우니까', 'Eomi'))]

        >>> lemmatizer.conjugate('차갑', '우니까')
        $ ['차가우니까', '차갑우니까']

    """

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
        """
        Arguments
        ---------
        verbs, adjectives, eomis : set of str
            Dictionary set
            If they are None, use trained dictionary.
            They are passed from __init__ function.

        Returns
        -------
        verbs, adjectives, eomis : set of str
            If each set is None, use trained dictionary with loading function.
        """

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
        """
        Arguments
        ---------
        path : str
            Dictionary file path

        Dictionary file can have information column such as word count
        For example,

            가 100
            먹 100
            시키 50

        However, it load only words, the first column in the file.

        Returns
        -------
        morphs : set of str
            Loaded dictionary
        """

        with open(path, encoding='utf-8') as f:
            morphs = {morph.split()[0] for morph in f}
        return morphs

    def _check_rules(self, lemma_rules, dictionary_name):
        """
        Arguments
        ---------
        lemma_rules : dict
            Dictionary of lemmatization rules.
            Passed from __init__ function

        Returns
        -------
        lemma_rules : dict
        conjugate_rules : dict
            Inverse mapper of lemma_rules
        """

        if lemma_rules is None:
            lemma_rules = self._load_rules(
                '{}/soylemma/dictionary/{}/rules.txt'.format(
                    installpath, dictionary_name))
        conjugate_rules = to_conjugate_rules(lemma_rules)
        return lemma_rules, conjugate_rules

    def _load_rules(self, path):
        """
        Arguments
        ---------
        path : str
            File path of rule table

        Rule table must have three column
        <surfacial form, canonical form of stem, canonical form of eomi>
        For example,

            했던 하 았던

        Returns
        -------
        lemma_rules : dict
        """

        with open(path, encoding='utf-8') as f:
            lines = [l.split() for l in f]
        lines = [(l[0], l[1], '아') if len(l) == 2 else l for l in lines]

        # 했던 -> (하, 았던)
        lemma_rules = defaultdict(lambda: set())
        for surf, stem, eomi in lines:
            lemma_rules[surf].add((stem, eomi))
        return dict(lemma_rules)

    def add_words(self, words, tag):
        """
        Arguments
        ---------
        words : collection of str
            Words
        tag : str
            Tag. choice from ['Adjective', 'Verb', 'Eomi']
        """

        # check words
        if isinstance(words, str):
            words = {words}

        if tag == ADJECTIVE:
            self.adjectives.update(words)
        elif tag == VERB:
            self.verbs.update(words)
        elif tag == EOMI:
            self.eomis.update(words)
        else:
            raise ValueError("You put wrong tag '{}'. Acceptable only ['Adjective', 'Verb', 'Eomi']".format(tag))

    def add_lemma_rules(self, rules):
        """
        Arguments
        ---------
        rules : lemma_rules
            Format example,

            lemma_rules = {
                '했': {('하', '았')},
                '끔': {('끈', 'ㅁ'), ('끌', 'ㅁ')}
                '가우니': {('갑', '니')} # 차가우니까 -> 차갑 + 니까
                ...
            }

        It first check input format, and update (lemma rules, conjugate rules) both
        """

        rules = check_rules(rules)
        self.lemma_rules = update_rules(self.lemma_rules, rules)

        supplements = to_conjugate_rules(rules)
        self.conjugate_rules = update_rules(self.conjugate_rules, supplements)

    def analyze(self, word, debug=False):
        """
        Arguments
        ---------
        word : str
            A word to perform morphological analysis
        debug : Boolean
            If True, verbose on

        Returns
        -------
        morphemes : list of tuple

        Usage
        -----
            >>> lemmatizer.analyze('차가우니까')
            $ [(('차갑', 'Adjective'), ('우니까', 'Eomi'))]
        """

        return analyze_morphology(
            word, self.verbs, self.adjectives,
            self.eomis, self.lemma_rules, debug)

    def lemmatize(self, word):
        """
        Arguments
        ---------
        word : str
            A word to recover canonical form (lemma)

        Returns
        -------
        morphemes : list of tuple

        Usage
        -----
            >>> lemmatizer.lemmatize('차가우니까')
            $ [('차갑다', 'Adjective')]
        """

        morphs = analyze_morphology(
            word, self.verbs, self.adjectives,
            self.eomis, self.lemma_rules)
        lemmas = [(stem[0]+'다', stem[1]) for stem, eomi in morphs]
        return lemmas

    def conjugate(self, stem, eomi):
        """
        Arguments
        ---------
        stem : str
        eomi : str

        Returns
        -------
        conjugated form : list of str

        Usage
        -----
            >>> lemmatizer.conjugate('차갑', '우니까')
            $ ['차가우니까', '차갑우니까']
        """

        return get_conjugate_candidates(stem, eomi, self.conjugate_rules)

def to_conjugate_rules(lemma_rules):
    # (하, 았) -> [했]
    conjugate_rules = defaultdict(lambda: set())
    for surf, canons in lemma_rules.items():
        for stem, eomi in canons:
            conjugate_rules[(stem, eomi)].add(surf)
    return dict(conjugate_rules)

def analyze_morphology(word, verbs, adjectives, eomis, lemma_rules, debug=False):
    """
    Arguments
    ---------
    word : str
        A word to analyze its morphology
    verbs : set of str
        Verb dictionary
    adjectives : set of str
        Adjective dictionary
    eomis : set of str
        Eomi dictionary
    lemma_rules : dict of tuple
        Lemmatization rules
    debug : Boolean
        If True, it prints all candidates

    Returns
    -------
    morphs : list of tuple
        For example,

            word = '파랬던'
            morphs = [(('파랗', 'Adjective'), ('았던', 'Eomi'))]

        Dictionary checked list of (stem, eomi)

    Function get_lemma_candidates returns set of (stem, eomi) candidates.
    This function checks whether the stem and eomi is known words using dictionaries.
    """

    morphs = []
    for stem, eomi in get_lemma_candidates(word, lemma_rules, debug):
        if not (eomi in eomis):
            continue
        if stem in adjectives:
            morphs.append(((stem, ADJECTIVE), (eomi, EOMI)))
        if stem in verbs:
            morphs.append(((stem, VERB), (eomi, EOMI)))
    return morphs

def get_lemma_candidates(word, rules, debug=False):
    """
    Arguments
    ---------
    word : str
        A word to analyze its morphology
    rules : dict of tuple
        Lemmatization rules

    Returns
    -------
    morphs : list of tuple
        All possible subword combination satisfying lemmatization rules


    용언이 활용되는 지점은 어간과 어미가 만나는 지점으로, 표현형 (surfacial form) 에서
    활용이 되는 지점의 길이에 따라 모든 경우를 확인한다.

    # 1 음절만 활용되는 경우
    - `했 = 하 + 았`
        - 시작했으니까 = 시작하 + 았으니까
    - `랬 = 랗 + 았`
        - 파랬던 = 파랗 + 았던

    # 2 음절만 활용되는 경우
    - `추운 = 춥 + 은`
        - 추운데 = 춥 + 은데
    - `했다 = 하 + 았다`
        - 시작했다 = 시작하 + 았다

    # 3 음절만 활용되는 경우
    - `가우니 = 갑 + 니`
        - 차가우니까 = 차갑 + 니까

    Debug mode 에서는 단어의 활용 지점과 단어의 어간, 어미 조합 후보를 출력한다.

        >>> lemmatizer = Lemmatizer(dictionary_name='demo')
        >>> lemmatizer.analyze('파랬다', debug=True)

        $ [DEBUG] word: 파랬다 = 파랗 + 았다, conjugation: 랬 = 랗 + 았
    """

    def debug_on(word, l, stem, eomi, r, conj):
        args = (word, l+stem, eomi+r, conj, stem, eomi)
        print('[DEBUG] word: {} = {} + {}, conjugation: {} = {} + {}'.format(*args))

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
                if debug:
                    debug_on(word, l_, stem, eomi, r, c)

        # 2 or 3 syllables conjugation
        for conj in {word[i:i+2], word[i:i+3]}:
            for stem, eomi in rules.get(conj, {}):
                candidates.append((l_ + stem, eomi + r[1:]))
                if debug:
                    debug_on(word, l_, stem, eomi, r[1:], conj)
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

def check_rules(rules):
    def type_error():
        raise ValueError("Wrong format inserted rules. rules={surface:{(stem, eomi), (stem, eomi), ...}}")

    rules_ = {}
    try:
        for surface, canons in rules.items():
            if isinstance(canons, str) or not isinstance(surface, str):
                type_error()
            canons_ = set()
            for canon in canons:
                if not (len(canon) == 2 and isinstance(canon[0], str) and isinstance(canon[1], str)):
                    type_error()
                canons_.add((canon[0], canon[1]))
            rules_[surface] = canons_
        return rules_
    except Exception as e:
        raise ValueError(str(e))

def update_rules(base, supplement):
    for surface, supple_set in supplement.items():
        base_set = base.get(surface, set())
        base_set.update(supple_set)
        base[surface] = base_set
    return base
