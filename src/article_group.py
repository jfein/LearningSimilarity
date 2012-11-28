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
        if self.svm_ready is None:
            self.svm_ready= []
            for source_data in self.texts.values():
                for article in source_data[1]:
                    numbered_examples= (article[0], [])
                    for ex in article[1]:
                        if ex[0] not in self.word_dictionary:
                            self.word_dictionary[ex[0]] = self.dict_size
                            self.dict_size += 1

                        numbered_examples[1].append((self.word_dictionary[ex[0]],ex[1]))

                numbered_examples[1].sort()
                self.svm_ready.append(numbered_examples)

            random.shuffle(self.svm_ready)

        return self.svm_ready

    def add_example(self, source, keywords, counter):
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
    ag= ArticleGroup()
    candidate_articles= range(source_articles.count)
    random.shuffle(candidate_articles)
    print candidate_articles
    length = 0
    for i in candidate_articles:
        if length == max_classes:
            return ag

        for _ in xrange(max_ex_per_class):
            bag= []
            for sentence in source_articles.spin_article(i):
                bag += sentence.split(' ')

            ag.add_example(i, source_articles.get_keywords(i), Counter(bag))

        length += 1

    return ag

#def create_keyword_article_group_from_sa():

if __name__ == "__main__":
    sa= SourceArticles()
    print sa.count
    ag= create_strict_article_group_from_sa(sa, 1000, 20)
    for ex in ag.svm_ready_examples:
        print "\n\n"
        print ex

    print ag.count_sources
    print ag.examples_per_source
