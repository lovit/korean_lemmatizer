class Lemmatizer:
    def __init__(self, verbs=None, adjectives=None, eomis=None, dictionary_name='demo'):

        verbs, adjectives, eomis = self._check_dictionary(
            verbs, adjectives, eomis, dictionary_name)

        self.verbs = verbs
        self.adjectives = adjectives
        self.eomis = eomis

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
            morphs = {morph.strip() for morph in f}
        return morphs