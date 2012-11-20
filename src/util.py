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
from nltk.corpus import wordnet


DATA_PATH = "../data/data.xml"
STOP_WORDS = "a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your".split(",")


class SourceArticles():

    @property
    def count(self):
        return len(self.articles)

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
    
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
                article_dict['keywords'] = self.standardize_words(kws)
                
                # Store keyword associations
                for word in article_dict['keywords']:
                    if word not in self.keywords:
                        self.keywords[word] = set()
                    self.keywords[word].add(cur_id)
                
                # Append article
                self.articles.append(article_dict)                
                cur_id += 1
            
    def standardize_words(self, text):
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
                lemmatized = self.lemmatize(word)
                if lemmatized not in STOP_WORDS and len(lemmatized) > 2:
                    words.add(lemmatized)
        return words
        
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
                
    def lemmatize(self, word):
        return self.lemmatizer.lemmatize(word)

    def get_keywords(self, num):
        return self.articles[num]['keywords']

    def get_title(self, num):
        return self.articles[num]['title']

    def get_article(self, num):
        return self.articles[num]['article']
        
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
        
    def _gen_phrases(self, s):
        exclude = set(string.punctuation) - set([' ', '|', '{', '}'])
        s = ''.join(ch for ch in s.lower() if ch not in exclude)
        crude_split = re.split("\{(.+?)\}", s)
        return [x.split("|") for x in crude_split if x.strip() != ""]
        
    def spin_articles(self, num, n=1):
        '''
        Returns list of n spun articles; articles produced will try to have
        lowest cos similarity; we use the heuristic of choosing a different 
        entry from each spin group with the assumption that it will lead to 
        some of the lowest cos similarity
        '''
        s = self.get_article(num)
        phrases = self._gen_phrases(s)

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
        phrases = self._gen_phrases(s)
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
    
    print "SOURCE TITLE:\n{0}\n".format(articles.get_title(article_num))
    print "SOURCE ARTICLE:\n{0}\n".format(articles.get_article(article_num))

    a = articles.spin_articles(article_num, 2)
    a1 = a[0]
    a2 = a[1]

    print "ARTICLE 1:\n{0}\n".format(a1)
    print "ARTICLE 2:\n{0}\n".format(a2)

    print "Cosine Similarity: {0}".format(cosine(a1, a2))