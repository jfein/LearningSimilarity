import random
from util import SourceArticles
from counter import Counter

class ArticleGroup():

    def __init__(self, keywords=None):
        self.keywords= keywords
        self.texts= {}
        self.svm_ready= None
        self.word_dictionary= {}
        self.dict_size= 0

    @property
    def count_sources(self):
        return len(self.texts)

    @property
    def examples_per_source(self):
        if len(self.texts.keys()):
            for key in self.texts.keys():
                return len(self.texts[key][1])
        else:
            return 0

    @property
    def svm_ready_examples(self):
        '''
        Flattens the examples and removes keyword data.  Replaces actual words
        with numbers.  Frequencies are converted to floats
        '''
        if self.svm_ready is None:
            self.svm_ready= []
            for source_data in self.texts.values():
                for article in source_data[1]:
                    numbered_examples= (article[0], [])
                    for ex in article[1]:
                        if ex[0] not in self.word_dictionary:
                            self.word_dictionary[ex[0]] = self.dict_size
                            self.dict_size += 1

                        numbered_examples[1].append((self.word_dictionary[ex[0]],float(ex[1])))

                    numbered_examples[1].sort()
                    self.svm_ready.append(numbered_examples)

        return self.svm_ready

    def add_example(self, source, keywords, counter):
        '''
        Puts a sinlge example article into the internal list of texts.  Source
        is the integer to index the article under (the index of its spin group),
        keywords are the keywords unique to this article (may be different than
        the keywords for the whole article group), and counter are the words in
        the article.
        '''
        examples= None
        if source not in self.texts:
            new_source= (keywords, [])
            self.texts[source]= new_source

        examples= self.texts[source][1]
        new_example= (source, [])
        for word in counter.keys():
            new_example[1].append((word, counter[word]))

        examples.append(new_example)

def create_strict_article_group_from_sa(source_articles, max_classes, max_ex_per_class):
    '''
    Creates an article group in which no effort is made to ensure that the
    sources are similar.  Therefore, it should be very easy to separate these
    classes, because they often do not share certain key words
    '''
    candidate_articles= range(source_articles.count)
    return article_group_from_candidates(source_articles, candidate_articles, max_classes,\
                                        max_ex_per_class)

def article_group_from_candidates(source_articles, candidate_articles, max_classes,\
                                  max_ex_per_class, keywords=None):
    '''
    Takes a number of spun articles (candidate articles) and puts them into an
    article group.  This involves flattening the sentences and putting them into
    a counter.  The keywords for the whole article group are also set
    '''
    ag= ArticleGroup(keywords)
    random.shuffle(candidate_articles)
    print candidate_articles
    length = 0
    for i in candidate_articles:
        if length == max_classes:
            return ag

        for article in source_articles.spin_articles(i, max_ex_per_class):
            bag= []
            for sentence in article:
                bag += sentence.split(' ')

            ag.add_example(i, source_articles.get_keywords(i), Counter(bag))

        length += 1

    return ag

def create_keyword_article_group_from_sa(source_articles, max_classes,\
                                         max_ex_per_class, keyword):
    '''
    More challenging than the strict group: all members of the article group
    have at least one keyword in common.  Should be harder to separate
    '''

    candidate_articles= get_articles_with_shared_keyword(keyword)
    article_group_from_candidates(source_articles, candidate_articles, max_classes,\
                                  max_ex_per_class, [keyword])

def create_all_matching_keywords_article_group_from_sa(source_articles, max_classes,\
                                                       max_ex_per_class, article_num,):
    '''
    Most challenging option.  All articles share all keywords.  Should hopefully
    replicate a realistic situation.
    '''

    candidate_articles= get_very_similar_articles(article_num)
    article_group_from_candidates(source_articles, candidate_articles, max_classes,max_ex_per_class,\
                                  source_articles.get_keywords(article_num))

if __name__ == "__main__":
    sa= SourceArticles()
    print sa.count
    ag= create_strict_article_group_from_sa(sa, 1000, 20)
    for ex in ag.svm_ready_examples:
        print "\n\n"
        print ex

    print ag.count_sources
    print ag.examples_per_source
