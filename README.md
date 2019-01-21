# 한국어 용언 분석기 (Korean Lemmatizer)

한국어의 동사와 형용사의 활용형 (surfacial form) 을 분석합니다. 한국어 용언 분석기는 다음의 기능을 제공합니다.

1. 입력된 단어를 어간 (stem) 과 어미 (eomi) 으로 분리
1. 입력된 단어를 원형으로 복원

## Usage

### analyze, lemmatize, conjugate

`analyze` function returns morphemes of the given predicator word

```python
from soylemma import Lemmatizer

lemmatizer = Lemmatizer()
lemmatizer.analyze('차가우니까')
```

The return value forms list of tuples because there can be more than one morpheme combination.

```
[(('차갑', 'Adjective'), ('우니까', 'Eomi'))]
```

`lemmatize` function returns lemma of the given predicator word.

```python
lemmatizer.lemmatize('차가우니까')
```

```
[('차갑다', 'Adjective')]
```

If the input word is not predicator such as Noun, it return empty list.

```python
lemmatizer.lemmatize('한국어') # []
```

`conjugate` function returns surfacial form. You should put stem and eomi as arguments. It returns all possible surfacial forms for the given stem and eomi.

```python
lemmatizer.conjugate(stem='차갑', eomi='우니까')
lemmatizer.conjugate('예쁘', '었던')
```

```
['차가우니까', '차갑우니까']
['예뻤던', '예쁘었던']
```

### update dictionaries and rules

For demonstration, we use dictioanry `demo`.

`어여뻤어` cannot be analyzed because the adjective `어여쁘` does not enrolled in dictionary.

```python
from soylemma import Lemmatizer

lemmatizer = Lemmatizer(dictionary_name='demo')
print(lemmatizer.analyze('어여뻤어')) # []
```

So, we add the word with tag using `add_words` function. Do it again. Then you can see the word `어여뻤어` is analyzed.

```python
lemmatizer.add_words('어여쁘', 'Adjective')
lemmatizer.analyze('어여뻤어')
```

```
[(('어여쁘', 'Adjective'), ('었어', 'Eomi'))]
```

However, the word `파랬다` is still not able to be analyzed because the lemmatization rule for surfacial form `랬` does not exist.

```python
lemmatizer.analyze('파랬다') # []
```

So, in this time, we update additional lemmatization rules using `add_lemma_rules` function.

```python
supplements = {
    '랬': {('랗', '았')}
}

lemmatizer.add_lemma_rules(supplements)
```

After that, we can see the word `파랬다` is analyzed, and also conjugation of `파랗 + 았다` is available.

```python
lemmatizer.analyze('파랬다')
lemmatizer.conjugate('파랗', '았다')
```

```
[(('파랗', 'Adjective'), ('았다', 'Eomi'))]
['파랬다', '파랗았다']
```

### debug on

If you wonder which subwords came up as candidates of (stem, eomi), use `debug`.

```python
lemmatizer.analyze('파랬다', debug=True)
```

```
[DEBUG] word: 파랬다 = 파랗 + 았다, conjugation: 랬 = 랗 + 았
[(('파랗', 'Adjective'), ('았다', 'Eomi'))]
```

### lemmatization rule extractor

You can extract lemmatization rule using `extract_rule` function.

```python
from soylemma import extract_rule

eojeol = '로드무비였다'
lw = '로드무비이'
lt = 'Adjective'
rw = '었다'
rt = 'Eomi'

extract_rule(eojeol, lw, lt, rw, rt)
```

```
('였다', ('이', '었다'))
```
