'''
Requires the following package:
https://github.com/martinblech/xmltodict
'''

import collections
import math
import re
import string
import random
import xmltodict
import codecs


DATA_PATH = "../data/data.xml"

'''
Problem: For xml entries that don't actually have any information 
(for example id 427 which has blank title, article) then there
will no #text entry for those columns, and get_title, get_article 
will raise a key error
'''
class SourceArticles():

    @property
    def count(self):
        return len(self.data['database']['table'])

    def __init__(self):
        self.data = xmltodict.parse(open(DATA_PATH, 'r'))
        non_empties = []
        for article_num, article in enumerate(self.data['database']['table']):
            for column in article['column'][0:4]:
                if not '#text' in column:
                    break
            else: #else clause only executed if we didn't break out
                non_empties.append(article_num)

        self.data['database']['table'] = [article for (article_num, article) in enumerate(self.data['database']['table']) if article_num in non_empties]


    def get_id(self, num):
        return self.data['database']['table'][num]['column'][0]['#text'].encode('utf-8')

    def get_keywords(self, num):
        return self.data['database']['table'][num]['column'][1]['#text'].encode('utf-8')

    def get_title(self, num):
        return self.data['database']['table'][num]['column'][2]['#text'].encode('utf-8')

    def get_article(self, num):
        return self.data['database']['table'][num]['column'][3]['#text'].encode('utf-8')

    # returns list of n spun articles; articles produced will have lowest cos similarity
    # note : lowest cos similarity is not guranteed. Rather we use the heuristic of choosing
    # a different entry from each spin group with the assumption that it will lead to some of the lowest
    # cos similarity
    def spin_articles(self, num, n=1):
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
        Return
        Number of spin groups in article
        Number of spin group elements
        Number of possible articles from each source article
        '''
        s = self.get_article(num)
        #s = "I {like|love|adore} all {animals|dogs|birds}. Nothing else {is cool|makes me happy}"
        phrases = gen_phrases(s)
        num_spin_groups = 0
        num_articles = 1
        total_spin_elements = 0

        for phrase in phrases:
            if len(phrase) > 1:
                # phrase is a spin group, and not constant phrase
                num_spin_groups += 1
                num_articles *= len(phrase)
                total_spin_elements += len(phrase)

        return num_spin_groups, total_spin_elements, num_articles


def gen_phrases(s):
            exclude = set(string.punctuation) - set([' ', '|', '{', '}'])
            s = ''.join(ch for ch in s.lower() if ch not in exclude)

            crude_split = re.split("\{(.+?)\}", s)

            return [x.split("|") for x in crude_split if x.strip() != ""]

def cosine(a, b):
    def dot(a, b):
        stop = "a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your".split(",")
        dot = 0
        for k, v in a.iteritems():
            if k in b and k not in stop:
                dot += a[k] + b[k]
        return float(dot)
    mag = lambda x : math.sqrt(dot(x, x))
    sim = lambda x, y : dot(x, y) / (mag(x) * mag(y))

    aa = collections.Counter(a.split())
    bb = collections.Counter(b.split())

    return sim(aa, bb)




if __name__ == "__main__":
    articles = SourceArticles()

    article_num = 5

    print "{0} TOTAL ARTICLES\n".format(articles.count)

    print "SOURCE TITLE:\n{0}\n".format(articles.get_title(article_num))
    print "SOURCE ARTICLE:\n{0}\n".format(articles.get_article(article_num))

    a = articles.spin_articles(article_num, 2)
    a1 = a[0]
    a2 = a[1]

    print "ARTICLE 1:\n{0}\n".format(a1)
    print "ARTICLE 2:\n{0}\n".format(a2)

    print "Cosine Similarity: {0}".format(cosine(a1, a2))
