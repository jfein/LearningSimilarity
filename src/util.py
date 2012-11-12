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


DATA_PATH = "..\data\data.xml"


class SourceArticles():
    
    @property
    def count(self):
        return len(self.data['database']['table'])

    def __init__(self):
        self.data = xmltodict.parse(open(DATA_PATH, 'r'))
   
    def get_id(self, num):
        return self.data['database']['table'][num]['column'][0]['#text'].encode('utf-8')
        
    def get_keywords(self, num):
        return self.data['database']['table'][num]['column'][1]['#text'].encode('utf-8')
        
    def get_title(self, num):
        return self.data['database']['table'][num]['column'][2]['#text'].encode('utf-8')

    def get_article(self, num):
        return self.data['database']['table'][num]['column'][3]['#text'].encode('utf-8')
        
    # returns list of n spun articles; articles produced will have lowest cos similarity
    def spin_articles(self, num, n=1):    
        def gen_phrases(s):
            exclude = set(string.punctuation) - set([' ','|','{','}'])
            s = ''.join(ch for ch in s.lower() if ch not in exclude)

            crude_split = re.split("\{(.+?)\}", s)

            return [x.split("|") for x in crude_split if x.strip() != ""]
            
        s = self.get_article(num)
        phrases = gen_phrases(s)

        articles = []
        for i in range(n):
            str = []
            for phrase in phrases:
                if len(phrase) != 0:
                    p = random.choice(phrase)
                    str.append(p.strip())
                    phrase.remove(p)
            articles.append(" ".join(str))
            
        return articles
   
       
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