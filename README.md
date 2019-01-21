# 한국어 용언 분석기 (Korean Lemmatizer)

한국어의 동사와 형용사의 활용형 (surfacial form) 을 분석합니다. 한국어 용언 분석기는 다음의 기능을 제공합니다.

1. 입력된 단어를 어간 (stem) 과 어미 (eomi) 으로 분리
1. 입력된 단어를 원형으로 복원

## Usage

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