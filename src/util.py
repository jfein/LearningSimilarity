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
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import sent_tokenize


DATA_PATH = "../data/data.xml"
STOP_WORDS = stopwords.words("english")


class SourceArticles():

    @property
    def count(self):
        return len(self.articles)

    def __init__(
            self,
            stdize_kws=True
        ):

        self.stemmer = WordNetLemmatizer()

        data = xmltodict.parse(open(DATA_PATH, 'r'))

        self.articles = []
        self.keywords = {}

        # Only use article if it has text in the article and is NOT NESTED
        cur_id = 0
        for article in data['database']['table']:
            article_body = article['column'][3].get('#text', 'null').encode('utf-8')
            if article_body.lower() != 'null' and not self.is_nested(article_body):
                # Make a simple dict for the article's data
                article_dict = {'article' : article_body}

                # Add in title info
                t = article['column'][2].get('#text', "").encode('utf-8')
                article_dict['title'] = t if t.lower() != "null" else ""

                # Add in keyword info
                kws = article['column'][1].get('#text', "").encode('utf-8')
                kws = kws if kws.lower() != "null" else ""
                article_dict['keywords'] = self.format_kws(kws, stdize_kws)


                # Store keyword associations
                for word in article_dict['keywords']:
                    if word not in self.keywords:
                        self.keywords[word] = set()
                    self.keywords[word].add(cur_id)

                # Append article
                self.articles.append(article_dict)
                cur_id += 1

    def format_kws(self, text, stdize_kws):
        '''
        Turns a text into a set of standard lemmatized words
        Words returned ONLY if alphabetic, more than 2 chars, and not stop word
        '''
        words = set()

        # Format text
        text = text.lower().replace("|", " ").replace(",", " ").replace("{", "").replace("}", "")

        # Add each valid lemmatized word in each keyword phrase
        for word in text.split(' '):
            word = word.strip()
            if bool(re.match('[a-z]+$', word, re.IGNORECASE)):
                if (stdize_kws):
                    word = self.stdize_word(word)
                if word not in STOP_WORDS and len(word) > 2:
                    words.add(word)
        return words

    def stdize_word(self, word):
        return self.stemmer.lemmatize(word)

    def is_nested(self, text):
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

    def get_article_sentences(self, num):
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

        article_body = self.articles[num]['article']
        sentences = sent_tokenize(article_body)

        parsed_sentences = []

        for sentence in sentences:
            spin_groups = gen_phrases(sentence)

            parsed_spin_groups = []
            if num == 4:
                print sentence
                print 't', spin_groups
            for spin_group in spin_groups:
                parsed_spin_group = []

                if num == 4:
                    print '\t', spin_group
                for phrase in spin_group:
                    parsed_spin_group.append(tuple(x.strip() for x in phrase.split()))

                parsed_spin_groups.append(frozenset(parsed_spin_group))

            parsed_sentences.append(parsed_spin_groups)

        return parsed_sentences

    def get_similar_articles(self, num):
        '''
        Returns a list of articles with at least 1
        keyword in common to article num
        '''
        kws = self.get_keywords(num)
        similar_articles = set()
        for kw in kws:
            similar_articles.update(self.keywords.get(kw, set()))
        if num in similar_articles:
            similar_articles.remove(num)
        return similar_articles

    def spin_articles(self, num, n=1):
        '''
        Returns list of n spun articles; articles produced will try to have
        lowest cos similarity; we use the heuristic of choosing a different 
        entry from each spin group with the assumption that it will lead to 
        some of the lowest cos similarity
        '''
        s = self.get_article(num)
        phrases = gen_phrases(s)

        articles = []
        for i in range(n):
            str = []
            for phrase in phrases:
                if len(phrase) > 1:
                    p = random.choice(phrase)
                    str.append(p.strip())
                    phrase.remove(p)
                else:
                    str.append(phrase[0].strip())
            articles.append(" ".join(str))

        return articles

    def get_stats(self, num):
        '''
        Returns
        Number of spin groups in article
        Number of spin group elements
        Number of possible articles from each source article
        '''
        s = self.get_article(num)
        phrases = self.gen_phrases(s)
        num_spin_groups = 0
        num_articles = 1
        total_spin_elements = 0

        for phrase in phrases:
            # phrase is a spin group, and not constant phrase
            if len(phrase) > 1:
                num_spin_groups += 1
                num_articles *= len(phrase)
                total_spin_elements += len(phrase)

        return num_spin_groups, total_spin_elements, num_articles


def cosine(a, b):
    def dot(a, b):
        dot = 0
        for k, v in a.iteritems():
            if k in b and k not in STOP_WORDS:
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
    exclude = set(string.punctuation) - set([' ', '|', '{', '}'])
    s = ''.join(ch for ch in s.lower() if ch not in exclude)
    crude_split = re.split("\{(.+?)\}|(\w+)", s)
    return [x.split("|") for x in crude_split if x and x.strip() != ""]


if __name__ == "__main__":
    articles = SourceArticles()

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

    article_num = 0

    print "SOURCE TITLE:\n{0}\n".format(articles.get_title(article_num))
    print "SOURCE ARTICLE:\n{0}\n".format(articles.get_article(article_num))

    a = articles.spin_articles(article_num, 2)
    a1 = a[0]
    a2 = a[1]

    print "ARTICLE 1:\n{0}\n".format(a1)
    print "ARTICLE 2:\n{0}\n".format(a2)

    print "Cosine Similarity: {0}".format(cosine(a1, a2))

    print "\n\n\nTesting Get Article Sentences\n\n"



    for article_num in xrange(5):
        print '\n\nArticle num', article_num
        sentences = articles.get_article_sentences(article_num)

        for sentence in sentences:
            print sentence


