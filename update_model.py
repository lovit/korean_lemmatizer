import argparse
import os
import soylemma
from soylemma import train_model_using_sejong_corpus_cleaner

def prune_dictionary(dic, min_count):
    return {w:c for w,c in dic.items() if c >= min_count}

def save_dictionary(dic, path):
    with open(path, 'w', encoding='utf-8') as f:
        for morpheme, count in sorted(dic.items()):
            f.write('{} {}\n'.format(morpheme, count))

def save_rules(rules, path):
    with open(path, 'w', encoding='utf-8') as f:
        for surface, canons in sorted(rules.items()):
            for l, r in sorted(canons):
                f.write('{} {} {}\n'.format(surface, l, r))

def save_exceptions(exceptions):
    with open('exception_cases_logs', 'w', encoding='utf-8') as f:
        for exception, count in sorted(exceptions.items(), key=lambda x:-x[1]):
            exception_strf = ', '.join(exception)
            f.write('{}\t{}\n'.format(exception_strf, count))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sejong_corpus_cleaner_repository', type=str, default='../sejong_corpus_cleaner/',
        help='Local repository path of https://github.com/lovit/sejong_corpus_cleaner/')
    parser.add_argument('--corpus_type', type=str, default='type3', choices=['type1', 'type2', 'type3'],
        help='L-R corpus type')
    parser.add_argument('--min_count', type=int, default=1, help='Minimum frequency of morphemes in dictionary')
    parser.add_argument('--dictionary_name', type=str, default='default', help='Dictioanry name')

    args = parser.parse_args()
    local_repository_path = args.sejong_corpus_cleaner_repository
    corpus_type = args.corpus_type
    min_count = args.min_count
    dictionary_name = args.dictionary_name
    dictionary_path = './soylemma/dictionary/{}/'.format(dictionary_name)
    if not os.path.exists(dictionary_path):
        os.makedirs(dictionary_path)

    table_path = '{}/data/clean/counter_{}_pair_all.txt'.format(local_repository_path, corpus_type)
    parameters = train_model_using_sejong_corpus_cleaner(local_repository_path, table_path)
    adjectives, verbs, eomis, rules, exceptions, lemmatizing_count = parameters

    save_dictionary(prune_dictionary(adjectives, min_count),  '.{}Adjectives.txt'.format(dictionary_path))
    save_dictionary(prune_dictionary(verbs, min_count),  '{}Verbs.txt'.format(dictionary_path))
    save_dictionary(prune_dictionary(eomis, min_count),  '{}Eomis.txt'.format(dictionary_path))
    save_rules(rules, '{}rules.txt'.format(dictionary_path))
    if exceptions:
        save_exceptions(exceptions)

if __name__ == '__main__':
    main()
