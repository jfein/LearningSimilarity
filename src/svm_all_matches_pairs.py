from svm_utils import subsets, five_fold_validation_check_same_source,\
        normalize, find_best_pair_test
from article_group import ArticleGroup, create_all_matching_keywords_article_group_from_sa
from util import SourceArticles

value = 3
thresholds= [0]
c_values= [.001, .01, .1, 1, 5, 10]

def get_results(ag, label):
    accuracy, false_positives, false_negatives, c_value= find_best_pair_test(ag, c_values,\
                                                                             thresholds)
    print ""
    #print stuff here
    print "Permutation: " + label
    print "Accuracy: " + str(accuracy)
    print "False positives: " + str(false_positives)
    print "False negatives: " + str(false_negatives)
    print "c_value: " + str(c_value)
    print ""

def try_stuff(sa, label):
    for i in xrange(sa.count):
        ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 5, i)
        if ag.count_sources > value:
            keyword_list= ""
            for word in list(sa.get_keywords(i)):
                keyword_list+= " " + word

            get_results(ag, label+  ", keywords= " + keyword_list + ", article number\
                      =" + str(i))

sa= SourceArticles()
try_stuff(sa, "No specials")


#repeat many times...
sa= SourceArticles(omit_stopwords=True)
try_stuff(sa, "No stopwords")


sa= SourceArticles(stdize_article=True)
try_stuff(sa, "stdize only")


sa= SourceArticles(stdize_kws=True)
try_stuff(sa, "kws only")


sa= SourceArticles(replace_with_synonyms=True)
try_stuff(sa, "synonyms only")


sa= SourceArticles(omit_stopwords=True, stdize_article=True)
try_stuff(sa, "stopwords and stdize")


sa= SourceArticles(omit_stopwords=True, stdize_kws=True)
try_stuff(sa, "stopwords and kws")


sa= SourceArticles(omit_stopwords=True, replace_with_synonyms=True)
try_stuff(sa, "stopwords and synonyms")


sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True, replace_with_synonyms=True)
try_stuff(sa, "everything")


sa= SourceArticles(stdize_article=True, stdize_kws=True)
try_stuff(sa, "stdize and kws")


sa= SourceArticles(stdize_article=True, stdize_kws=True, replace_with_synonyms=True)
try_stuff(sa, "everything but stopwords")


sa= SourceArticles(stdize_article=True, replace_with_synonyms=True)
try_stuff(sa, "stdize and synonyms")


sa= SourceArticles(stdize_kws=True, replace_with_synonyms=True)
try_stuff(sa, "kws and synonyms")



sa= SourceArticles(omit_stopwords=True, stdize_kws = True, replace_with_synonyms=True)
try_stuff(sa, "without stdize")


sa= SourceArticles(omit_stopwords=True, stdize_article=True, replace_with_synonyms=True)
try_stuff(sa, "without kws")

sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True)
try_stuff(sa, "without synonyms")
