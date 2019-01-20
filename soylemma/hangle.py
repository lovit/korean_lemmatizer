import re


hangle_pattern = re.compile('[가-힣]+')

def is_hangle(word):
    match = hangle_pattern.match(word)
    if not match:
        return False
    span = match.span()
    return (span[1] - span[0]) == len(word)

def compose(cho, jung, jong):
    """
    Arguments
    ---------
    cho : str
        Chosung, length is 1
    jung : str
        Jungsung, length is 1
    jong : str
        Jongsung, length is 1

    Returns
    -------
    Composed hangle : str
    """

    cho_ = cho_to_idx.get(cho, -1)
    jung_ = jung_to_idx.get(jung, -1)
    jong_ = jong_to_idx.get(jong, -1)
    if (cho_ < 0) or (jung_ < 0) or (jong_ < 0):
        return None
    return chr(kor_begin + cho_base * cho_ + jung_base * jung_ + jong_)

def decompose(input, ensure_input=False):
    """
    Arguments
    ---------
    input : str
        Character, length is 1
    ensure_input : Boolean
        If True, pass length and hangle check

    Returns
    -------
    (cho, jung, jong) : tuple of str or None
        If input is hangle.
        Else it return None
    """

    if not ensure_input:
        if len(input) > 1 or not is_hangle(input):
            return None
    i = ord(input) - kor_begin
    cho  = i // cho_base
    jung = ( i - cho * cho_base ) // jung_base
    jong = ( i - cho * cho_base - jung * jung_base )
    return (chosungs[cho], jungsungs[jung], jongsungs[jong])

kor_begin = 44032
kor_end = 55203
cho_base = 588
jung_base = 28
jaum_begin = 12593
jaum_end = 12622
moum_begin = 12623
moum_end = 12643

# 19 characters
chosungs = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ',
    'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ',
    'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

# 21 characters
jungsungs = [
    'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ',
    'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
    'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ',
    'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
    'ㅣ'
]

# 28 characters including white space
jongsungs = [
    ' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ',
    'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ',
    'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ',
    'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ',
    'ㅌ', 'ㅍ', 'ㅎ'
]

# 30 characters
jaums = [
    'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ',
    'ㄶ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㄺ',
    'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ',
    'ㅀ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅄ',
    'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ',
    'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

# 21 characters
moums = [
    'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ',
    'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
    'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ',
    'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
    'ㅣ'
]

cho_to_idx = {cho:idx for idx, cho in enumerate(chosungs)}
jung_to_idx = {jung:idx for idx, jung in enumerate(jungsungs)}
jong_to_idx = {jong:idx for idx, jong in enumerate(jongsungs)}