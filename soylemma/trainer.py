from collections import defaultdict
from .hangle import decompose

is_jaum = lambda c: 'ㄱ' <= c <= 'ㅎ'
is_moum = lambda c: 'ㅏ' <= c <= 'ㅣ'

def parse(line):
    eojeol, morphtags, count = line.strip().split('\t')
    morphtags = [mt.rsplit('/', 1) for mt in morphtags.split(' + ')]
    count = int(count)
    return eojeol, morphtags, count

def _right_form(morph):
    """
    Arguments
    ---------
    morph : str
        Morpheme str

    Returns
    -------
    형태소의 첫 글자가 모음, 두번째 글자가 자음이면 False, 그 외에는 True
    eg)
        eojeol = '갔다가'
        morphemes = '가/VV + ㅏㅆ/EP + 다가/EC'

    Usage
    -----
        print(_right_form('ㅏㅆ)) # False
        print(_right_form('다가)) # True
    """

    if is_moum(morph[0]) and len(morph) > 1 and is_jaum(morph[1]):
        return False
    return True

def right_form(morphemes):
    for morph, _ in morphemes:
        if not _right_form(morph):
            return False
    return True

def load_word_morpheme_table(path):
    """
    Arguments
    ---------
    path : str
        Eojeol, Morpheme, Count table

        File example, 

            개봉된	개봉되/Verb + ㄴ/Eomi	17
            개봉될	개봉되/Verb + ㄹ/Eomi	7
            개봉인	개봉이/Adjective + ㄴ/Eomi	2
            ...

    Returns
    -------
    eojeol_to_morphemes : list of tuple

        For example,

        eojeol_to_morphemes = [
            ...
            ('개정하면서', [['개정하', 'Verb'], ['면서', 'Eomi']]),
            ('개정하여', [['개정하', 'Verb'], ['아', 'Eomi']]),
            ('개정하자는', [['개정하', 'Verb'], ['자는', 'Eomi']])
            ...
        ]
    """
    # Eojeol, Morpheme, Count
    eojeol_to_morphemes = {}
    with open(path, encoding='utf-8') as f:
        next(f)
        for line in f:
            eojeol, morphemes, count = parse(line)
            if not right_form(morphemes):
                continue
            if eojeol in eojeol_to_morphemes:
                continue
            eojeol_to_morphemes[eojeol] = morphemes
    eojeol_to_morphemes = list(eojeol_to_morphemes.items())
    return eojeol_to_morphemes

def extract_rule(eojeol, lw, lt, rw, rt):
    """
    Arguments
    ---------
    eojeol : str
        Eojeol
    lr : str
        Left-side morpheme
    lt : str
        Tag of left-side morpheme
    rw : str
        Right-side morpheme
    rt : str
        Tag of right-side morpheme

    Returns
    -------
    surface, canon : str, (str, str) or None
        If the eojeol is conjugated it return surface & canon tuple
        Else, it return None

    Usage
    -----
        >>> extract_rule('가까웠는데', '가깝', 'Adjective', '었는데', 'Eomi')
        $ ('까웠', ('깝', '었는'))

        >>> extract_rule('가까워지며', '가까워지', 'Verb', '며', 'Eomi')
        $ None
    """

    if not (lt == 'Adjective' or lt == 'Verb'):
        return
    if lw + rw == eojeol:
        return

    surface = eojeol[len(lw)-1:len(lw)+1]

    # extract_rule('어쩔', '어찌하', 'Verb', '알', 'Eomi')
    # extract_rule('이뤄진', '이루어지', 'Verb', 'ㄴ', 'Eomi')
    if not surface:
        def find_begin(eojeol, lw):
            for i, char in enumerate(eojeol):
                if char != lw[i]:
                    return i
            return i+1
        b = find_begin(eojeol, lw)
        if b == len(eojeol):
            return
        surface = eojeol[b:]
        canon = (lw[b:], rw[0])
    elif decompose(surface[0])[0] != decompose(lw[-1])[0]:
        return
    else:
        if len(lw) + len(rw) == len(eojeol):
            canon = (lw[-1], rw[0])
        elif len(lw) + len(rw) > len(eojeol):
            canon = (lw[-1], rw[:2])
        elif len(lw) + len(rw) + 1 == len(eojeol):
            surface = eojeol[len(lw)-1:len(lw)+2]
            canon = (lw[-1], rw[0])
        else:
            raise ValueError('처리 불가. eojeol={}, {}/{} + {}/{}'.format(eojeol, lw, lt, rw, rt))

    # post-processing: Ignore exception
    if len(surface) == 2 and len(canon[0]) == 1 and len(canon[1]) == 1:
        surf_cho_l = decompose(surface[0])[0]
        surf_cho_r, _, surf_jong_r = decompose(surface[1])
        canon_cho_l = decompose(canon[0][0])[0]
        canon_cho_r, canon_jung_r, canon_jong_r = decompose(canon[1][0])

        # 원형과 표현형의 어간 마지막 글자의 초성이 같은지 확인
        if surf_cho_l != canon_cho_l:
            raise ValueError('어간 마지막 글자의 초성이 다른 경우 eojeol={}, {}/{} + {}/{}'.format(eojeol, lw, lt, rw, rt))
        # 원형과 표현형의 어미 첫글자의 초성이 같거나, 어미의 첫글자가 자음일 때 종성이 같은지 확인
        if not ((surf_cho_r == canon_cho_r) or (canon_jung_r == ' ' and surf_jong_r == canon_cho_r)):
            if canon_cho_r != 'ㅇ' and not (surf_cho_r == 'ㅊ' and canon_cho_r == 'ㅈ'):
                raise ValueError('어미 첫글자의 초성이 다른 경우 eojeol={}, {}/{} + {}/{}'.format(eojeol, lw, lt, rw, rt))

    return surface, canon

def extract_rules(eojeol_lr_array):
    """
    Arguments
    ---------
    eojeol_lr_array : nested list

        [
            (Eojeol, ((lw, lt), (rw, rt))),
            (Eojeol, ((lw, lt), (rw, rt))),
            ...
        ]
        All Eojeol, lw, lt, rw, rt is str type

    Returns
    -------
    rules : dict of set
        Lemmatizing rule
        rules = {
            '했던': {('하', '았던')},
            '인': {('이', 'ㄴ')},
            ...
        }

    Usage
    -----
        eojeol_lr_array = [
            ('가당하시냐고', [['가당하', 'Adjective'], ['시냐고', 'Eomi']])
            ('가당하지', [['가당하', 'Adjective'], ['지', 'Eomi']])
            ('가당한', [['가당하', 'Adjective'], ['ㄴ', 'Eomi']])
            ('가닿는', [['가닿', 'Verb'], ['는', 'Eomi']])
            ('가닿는다는', [['가닿', 'Verb'], ['는다는', 'Eomi']])
            ...
        ]

        rules = extract_rules(eojeol_lr_array)
    """

    rules = defaultdict(lambda: set())
    for eojeol, ((lw, lt), (rw, rt)) in eojeol_lr_array:
        try:
            rule = extract_rule(eojeol, lw, lt, rw, rt)
            if rule is None:
                continue
            surface, canon = rule
            rules[surface].add(canon)
        except Exception as e:
            print(e)
            print(eojeol, ((lw, lt), (rw, rt)), end='\n\n')
    return dict(rules)

def train_model_using_sejong_corpus_cleaner(local_repository_path, table_path, show_exception=False):
    """
    Arguments
    ---------
    local_repository_path : str
        Local repository path of https://github.com/loit/sejong_corpus_cleaner.git
    table_path : str
        Count table path
        A row in the table is formed such as ((Eojeol, MorphTags), count)
    show_exception : Boolean
        If True, it shows exception when it occurs

    Returns
    -------
    adjectives : {str:int}
        {morpheme:count}
    verbs : {str:int}
        {morpheme:count}
    eomis : {str:int}
        {morpheme:count}
    rules : dict of set
        rules = {
            '했던': {('하', '았던')},
            '인': {('이', 'ㄴ')},
            ...
        }
    exceptions : {tuple:int}
        {(eojeol, lw, lt, rw, rt):count}
    lemmatizing_count : int
        Total count of lemmatizing case

    Usage
    -----
        >>> local_repository_path = ''
        >>> table_path = ''
        >>> parameters = train_model_using_sejong_corpus_cleaner(local_repository_path, table_path)
        >>> adjectives, verbs, eomis, rules, exceptions, lemmatizing_count = parameters
    """

    import sys
    sys.path.append(local_repository_path)
    try:
        import sejong_corpus_cleaner
        from collections import defaultdict
    except Exception as e:
        print(e)
        raise ValueError('Failed to import sejong_corpus_cleaner package. Check local repository path')

    from sejong_corpus_cleaner.loader import load_count_table
    rows = load_count_table(table_path)

    eomis = defaultdict(int)
    adjectives = defaultdict(int)
    verbs = defaultdict(int)
    rules = defaultdict(lambda: set())
    exceptions = dict()

    lemmatizing_count = 0

    for (eojeol, morphtags), count in rows:
        if len(morphtags) == 1:
            continue
        (lw, lt), (rw, rt) = morphtags
        lemmatizing_count += count

        try:
            rule = extract_rule(eojeol, lw, lt, rw, rt)
            if rule is None:
                continue
            surface, canon = rule
            rules[surface].add(canon)
            if lt == 'Verb':
                verbs[lw] += count
            elif lt == 'Adjective':
                adjectives[lw] += count
            if rt == 'Eomi':
                eomis[rw] += count
        except Exception as e:
            if show_exception:
                print(e)
            exceptions[(eojeol, lw, lt, rw, rt)] = count

    adjectives, verbs, eomis = dict(adjectives), dict(verbs), dict(eomis)
    rules = dict(rules)

    exception_perc = 100 * sum(exceptions.values()) / lemmatizing_count
    args = (sum(len(v) for v in rules.values()), len(adjectives), len(verbs), len(eomis), len(exceptions), '%.3f' % exception_perc)
    print('Found {} rules, {} adjectives, {} verbs, {} eomis, with {} ({} %) exceptions'.format(*args))

    return adjectives, verbs, eomis, rules, exceptions, lemmatizing_count
