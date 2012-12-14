import os
from svm_utils import subsets, five_fold_validation_check_same_source,\
        normalize, find_best, subsets
from article_group import ArticleGroup, create_all_matching_keywords_article_group_from_sa
from util import SourceArticles

value = 2
thresholds= [float(x) / 200 for x in xrange(170, 202, 1)]
c_values= [.001, .01, .1, 1, 5, 10]
#c_values= [.01, .1]

def get_results(ag, label):
    if os.path.exists('positives.ex'):
        os.remove('positives.ex')
        os.remove('negatives.ex')

    train_sets, validation_sets, test_set= subsets(ag.svm_ready_examples, 5)
    for threshold in thresholds:
        accuracy, true_plus, true_minus, false_positives, false_negatives,\
                c_value= find_best(c_values, threshold, train_sets,\
                                   validation_sets,test_set)
        print str(threshold) + "\t" +\
                str(false_positives/(true_minus + false_negatives)) + "\t" +\
                str(true_plus/(true_plus + false_positives))


sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True, replace_with_synonyms=True)
for i in xrange(sa.count):
    ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
    if ag.count_sources > value:
        keyword_list= ""
        print "got here"
        for word in list(sa.get_keywords(i)):
            keyword_list+= " " + word

        get_results(ag, "everything, keywords= " + keyword_list + ", article number\
                    =" + str(i))
