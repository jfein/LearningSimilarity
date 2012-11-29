from svm_utils import subsets, five_fold_validation_check_same_source,\
        normalize, find_best_pair_test
from article_group import ArticleGroup, create_strict_article_group_from_sa
from util import SourceArticles

thresholds= [0]
c_values= [.001, .01, .1, 1, 5, 10]
#c_values= [.01, .1]

def get_results(sa, label):
  ag= create_strict_article_group_from_sa(sa, 1000, 5)
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

sa= SourceArticles()
get_results(ag, "No specials")

#repeat many times...
sa= SourceArticles(omit_stopwords=True)
get_results(sa, "Stopwords only")

sa= SourceArticles(stdize_article=True)
get_results(sa, "Stdize only")

sa= SourceArticles(stdize_kws=True)
get_results(sa, "keywords only")

sa= SourceArticles(replace_with_synonyms=True)
get_results(sa, "Synonyms only")

sa= SourceArticles(omit_stopwords=True, stdize_article=True)
get_results(sa, "Stopwords and stdize")


sa= SourceArticles(omit_stopwords=True, stdize_kws=True)
get_results(sa, "Stopwords and kws")

sa= SourceArticles(omit_stopwords=True, replace_with_synonyms=True)
get_results(sa, "Stopwords and synonyms")



sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True, replace_with_synonyms=True)
get_results(sa, "everything")

sa= SourceArticles(stdize_article=True, stdize_kws=True)
get_results(sa, "stdize and kws")

sa= SourceArticles(stdize_article=True, stdize_kws=True, replace_with_synonyms=True)
get_results(sa, "not stopwords")

sa= SourceArticles(stdize_article=True, replace_with_synonyms=True)
get_results(sa, "Stdize and synonyms")

sa= SourceArticles(stdize_kws=True, replace_with_synonyms=True)
get_results(sa, "kws and synonyms")


sa= SourceArticles(omit_stopwords=True, stdize_kws = True, replace_with_synonyms=True)
get_results(sa, "not stdize")

sa= SourceArticles(omit_stopwords=True, stdize_article=True, replace_with_synonyms=True)
get_results(sa, "not kws")

sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True)
get_results(sa, "not synonyms")
