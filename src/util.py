'''
Requires the following package:
    https://github.com/martinblech/xmltodict
    http://nltk.org/index.html
'''

import collections
import math
import re
import string
import random
import xmltodict
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import sent_tokenize


DATA_PATH = "../data/data.xml"
STOP_WORDS = stopwords.words("english")

WORD_NET_LEMMATIZER, PORTER_STEMMER = range(2)


class SourceArticles():

    @property
    def count(self):
        return len(self.articles)

    def __init__(
            self,
            stdizer=WORD_NET_LEMMATIZER,
            omit_stopwords=False,
            stdize_kws=True,
            stdize_article=False,
            max_phrase_size=None,
        ):

        self.omit_stopwords = omit_stopwords
        self.stdize_kws = stdize_kws
        self.stdize_article = stdize_article
        self.max_phrase_size = max_phrase_size
        
        if stdizer == WORD_NET_LEMMATIZER:
            self.stdize_word = WordNetLemmatizer().lemmatize
        elif stdizer == PORTER_STEMMER:
            self.stdize_word = PorterStemmer().stem
        
        data = xmltodict.parse(open(DATA_PATH, 'r'))

        self.articles = []
        self.keywords = {}

        # Only use article if it has text in the article and is NOT NESTED
        for article in data['database']['table']:
            article_body = article['column'][3].get('#text', 'null').encode('utf-8')
            if article_body.lower() != 'null':
                # Make a simple dict for the article's data
                article_dict = {'article' : article_body}

                # Add in title info
                t = article['column'][2].get('#text', "").encode('utf-8')
                article_dict['title'] = t if t.lower() != "null" else ""

                # Add in keyword info
                kws = article['column'][1].get('#text', "").encode('utf-8')
                kws = kws if kws.lower() != "null" else ""
                article_dict['keywords'] = self.format_kws(kws)

                # Store keyword associations
                for word in article_dict['keywords']:
                    if word not in self.keywords:
                        self.keywords[word] = set()
                    self.keywords[word].add(len(self.articles))

                # Append article
                self.articles.append(article_dict)
                
    def format_kws(self, kws):
        '''
        Turns a text into a set of standard lemmatized words
        Words returned ONLY if alphabetic, more than 2 chars, and not stop word
        '''
        words = set()

        # Format kws
        kws = kws.lower().replace("|", " ").replace(",", " ").replace("{", "").replace("}", "")

        # Add each valid word in each keyword phrase
        for word in kws.split(' '):
            word = word.strip()
            # TODO: make this better
            if bool(re.match('[a-z]+$', word, re.IGNORECASE)):
                if (self.stdize_kws):
                    word = self.stdize_word(word)
                if word not in STOP_WORDS and len(word) > 2:
                    words.add(word)
                    
        return words

    def get_keywords(self, num):
        '''
        Returns the set of article num's keywords
        '''
        return self.articles[num]['keywords']

    def get_title(self, num):
        '''
        Returns article num's title
        '''
        return self.articles[num]['title']

    def get_article(self, num):
        '''
        Returns article num's article body
        '''
        return self.articles[num]['article']

    def spin_article(self, num, article_body=None):
        '''
        Returns a generated spun article. Spun articles are 
        represented as a list of spun sentences. A spun 
        sentence is simply a string.
        
        So if article is "I {like|love} the {dog|canine}. He {likes|loves} the {cat|feline}"
        and n = 2, a possible result would be
        
        ["I like the canine", "He likes the cat"]
        '''
        article_sentences = self.get_article_sentences(num, article_body)

        spun_sentences = []
        for sentence in article_sentences:
            spun_sentence = []
            for spin_group in sentence:
                spin_group = list(spin_group)
                phrase = random.choice(spin_group)
                spun_sentence.append(" ".join(phrase).strip())
            spun_sentences.append(" ".join(spun_sentence))

        return spun_sentences

    def spin_dissimilar_articles(self, num, n=1, article_body=None):
        '''        
        Returns list of n spun articles; articles produced will try to have
        lowest cos similarity; we use the heuristic of choosing a different 
        entry from each spin group with the assumption that it will lead to 
        some of the lowest cos similarity
        
        So if article is "I {like|love} the {dog|canine}. He {likes|loves} the {cat|feline}"
        and n = 2, a possible result would be
        
        [["I like the canine", "He likes the cat"], ["I love the dog", "He loves the feline"]]
        
        Essentially spin_article_sentences but with the n parameter
        '''
        article_sentences = self.get_article_sentences(num, article_body)
        article_sentences_cpy = []
        for sentence in article_sentences:
            sentence_cpy = []
            for spin_group in sentence:
                sentence_cpy.append(list(spin_group))
            article_sentences_cpy.append(sentence_cpy)

        article_sentences = article_sentences_cpy

        spun_articles = []
        for _ in xrange(n):
            spun_sentences = []
            for sentence in article_sentences:
                spun_sentence = []
                for spin_group in sentence:
                    phrase = random.choice(spin_group)
                    spun_sentence.append(" ".join(phrase).strip())
                    if len(spin_group) > 1:
                        spin_group.remove(phrase)
                spun_sentences.append(" ".join(spun_sentence))
            spun_articles.append(spun_sentences)

        return spun_articles

    def get_article_sentences(self, num, article_body=None):
        '''
        Return article_num as a list of sentences. 
        Each sentence is represented as a list of spin groups. 
        Each spin group is represented as a frozenset of phrases
        Each phrase is represented as a tuple of words.
        
        So returns a set of list of list of sets of lists
        I {like|love} dogs. {They are|one is} great.
        
        [
        [Set([I]), SET([like], [love]), Set([dogs])],
        [Set([they, are], [one, is]), Set([great])]
        ]
        
        The words are standardized based on options passed
        to SourceArticles on construction.
        '''
        if not article_body:
            if 'article_sentences' in self.articles[num]:
                return self.articles[num]['article_sentences']

            # Use this flag since we can't use 'if not article_body' at the end
            # to determine whether to store results in the cache since
            # we're about to assign something to article_body
            store_in_cache = True
            article_body = self.articles[num]['article']
        else:
            store_in_cache = False
            article_body = article_body.lower()

        sentences = sent_tokenize(article_body)
        parsed_sentences = []

        for sentence in sentences:
            discard_sentence = False
            spin_groups = gen_phrases(sentence)

            if is_nested(sentence):
                continue

            parsed_spin_groups = []
            for spin_group in spin_groups:
                parsed_spin_group = []

                for phrase in spin_group:
                    if self.stdize_article:
                        words = (self.stdize_word(x.strip()) for x in phrase.split())
                    else:
                        words = (x.strip() for x in phrase.split())

                    words_tuple = tuple(word for word in words if (not self.omit_stopwords or word not in STOP_WORDS))

                    if self.max_phrase_size and len(words_tuple) > self.max_phrase_size:
                        # Just discard the whole sentence
                        discard_sentence = True
                    #Words tuple may be empty if it's just stopwords
                    if words_tuple:
                        parsed_spin_group.append(words_tuple)

                # Parsed spin group may be empty if we're omitting stopwords. Only add it if it is nonempty
                if parsed_spin_group:
                    parsed_spin_groups.append(frozenset(parsed_spin_group))
            if not discard_sentence:
                parsed_sentences.append(parsed_spin_groups)

        if store_in_cache:
            self.articles[num]['article_sentences'] = parsed_sentences

        return parsed_sentences

    def get_similar_articles(self, num):
        '''
        Returns a list of articles with at least 1
        keyword in common to article num
        '''
        kws = self.get_keywords(num)
        if not kws:
            return set()
        similar_articles = set()
        for kw in kws:
            similar_articles.update(self.keywords.get(kw, set()))
        if num in similar_articles:
            similar_articles.remove(num)
        return similar_articles

    def get_very_similar_articles(self, num):
        '''
        Returns a list of articles with all
        keywords in common to article num
        '''
        kws = self.get_keywords(num)
        if not kws:
            return set()
        similar_articles = self.keywords.get(kws.pop(), set())
        for kw in kws:
            similar_articles.intersection_update(self.keywords.get(kw, set()))
        if num in similar_articles:
            similar_articles.remove(num)
        return similar_articles

    def get_phrase_size_stats(self):
        max_phrase_size, max_group = 0, None
        counts = {}
        total = 0.0
        seen_phrases = set()
        for num in xrange(self.count):
            for sentence in self.get_article_sentences(num):
                for spin_group in sentence:
                    for phrase in spin_group:
                        phrase_size = len(phrase)
                        if phrase_size == 0 or phrase in seen_phrases:
                            continue
                        seen_phrases.add(phrase)
                        counts[phrase_size] = counts.get(phrase_size, 0) + 1
                        total += 1
                        if phrase_size > max_phrase_size:
                            max_phrase_size, max_phrase = phrase_size, phrase

        print "Max phrase size : ", max_phrase_size
        print max_phrase
        print ""
        for k, v in counts.iteritems():
            print "{0} : {1}".format(k, v)

        for k, v in counts.iteritems():
            print "{0} : {1}".format(k, v / total)

        cumulative = 0.0

        for k, v in counts.iteritems():
            cumulative += v / total
            print "{0} : {1}".format(k, cumulative)



def cosine(a, b):
    def dot(a, b):
        dot = 0
        for k, v in a.iteritems():
            if k in b:
                dot += a[k] + b[k]
        return float(dot)
    mag = lambda x : math.sqrt(dot(x, x))
    sim = lambda x, y : dot(x, y) / (mag(x) * mag(y))

    aa = collections.Counter(a.split())
    bb = collections.Counter(b.split())

    return sim(aa, bb)


def gen_phrases(s):
    '''
    Makes a set of phrases
    '''
    # TODO: make sure exclude set is OK
    exclude = set(string.punctuation) - set([' ', '|', '{', '}', '\''])
    s = ''.join(ch for ch in s.lower() if ch not in exclude)
    crude_split = re.split("\{(.+?)\}|(\w+)", s)

    return [ 
        k for k in 
            [ [w for w in x.split("|") if w] for x in crude_split if (x and x.strip()) ] 
        if k 
    ]


def is_nested(text):
    '''
    Returns true if text has a spin group within a spin group
    '''
    cnt = 0
    for ch in text:
        if ch == "{":
            cnt += 1
        if ch == "}":
            cnt -= 1
        if cnt > 1:
            return True
    return False



if __name__ == "__main__":
    articles = SourceArticles(            
            #stdizer=PORTER_STEMMER,
            omit_stopwords=True,
            stdize_article=True,
            max_phrase_size=None
    )

    '''
    print articles.get_article_sentences(1, article_body="I {like|love} the {dog|canine}. {He doesn't care for|He really does not care for|He really doesn't care for} the dog. She {like|love} the dumb dog")

    # Print all keywords
    for i in range(articles.count):
        print "ARTICLE {0}".format(i)
        for kw in articles.get_keywords(i):
            print "\t" + kw
    print "\n\n"
    # Print all keyword associations
    for keyword, nums in articles.keywords.iteritems():
        if len(nums) > 1:
            print "{0}\n\tARTICLES: {1}".format(keyword, nums)

    print "----------------------------------------------------"
    print "{0} TOTAL ARTICLES\n".format(articles.count)

    print articles.get_similar_articles(313)

    print "----------------------------------------------------"
    '''
    
    article_num = 0

    print "SOURCE ARTICLE:\n{0}\n".format(articles.get_article(article_num))

    a = articles.spin_dissimilar_articles(article_num, 2)
    a1 = " ".join(a[0])
    a2 = " ".join(a[1])

    print "ARTICLE 1:\n{0}\n".format(a1)
    print "ARTICLE 2:\n{0}\n".format(a2)

    print "Cosine Similarity: {0}".format(cosine(a1, a2))

    print "\n\n\nTesting Get Article Sentences\n\n"


