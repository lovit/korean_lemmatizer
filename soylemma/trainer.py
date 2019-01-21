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

    if is_moum(morph) and len(morph) > 1 and is_jaum(morph):
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
    surface, canon : str, str
        If the eojeol is conjugated it return surface & canon tuple
        Else, it return None

    Usage
    -----
        $ extract_rule('가까웠는데', '가깝', 'Adjective', '었는데', 'Eomi')
        > ('까웠', ('깝', '었는'))

        $ extract_rule('가까워지며', '가까워지', 'Verb', '며', 'Eomi')
        > None
    """

    if not (lt == 'Adjective' or lt == 'Verb'):
        return
    surface = eojeol[len(lw)-1:len(lw)+1]
    if decompose(surface[0])[0] != decompose(lw[-1])[0]:
        return
    if lw + rw == eojeol:
        return
    if len(lw) + len(rw) == len(eojeol):
        canon = (lw[-1], rw[0])
    elif len(lw) + len(rw) > len(eojeol):
        canon = (lw[-1], rw[:2])
    elif len(lw) + len(rw) + 1 == len(eojeol):
        canon = (lw[-1], eojeol[len(lw)]+rw[0])
    else:
        raise ValueError('처리 불가. eojeol={}, {}/{} + {}/{}'.format(eojeol, lw, lt, rw, rt))
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
            '했던': {'하았던'},
            '인': {'이ㄴ'},
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