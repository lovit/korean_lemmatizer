__author__ = 'lovit'
__name__ = 'soylemma: Korean trained lemmatizer'
__version__ = '0.1.1'

from .lemmatizer import Lemmatizer
from .lemmatizer import analyze_morphology
from .lemmatizer import get_lemma_candidates
from .hangle import compose
from .hangle import decompose
from .hangle import is_hangle
from .trainer import extract_rule
from .trainer import extract_rules
from .trainer import load_word_morpheme_table
from .trainer import train_model_using_sejong_corpus_cleaner
from .utils import installpath

# tagset
from .utils import ADJECTIVE
from .utils import VERB
from .utils import EOMI