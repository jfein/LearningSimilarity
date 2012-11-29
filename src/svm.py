from svm_utils import subsets, five_fold_validation_check_same_source,\
        normalize, find_best
from article_group import ArticleGroup, create_strict_article_group_from_sa
from util import SourceArticles

thresholds= [0]
c_values= [.0001, .001, .01, .1, 1, 5, 10]
#c_values= [.01, .1]

def get_results(ag, label):
  accuracy, false_positives, false_negatives, c_value= find_best(ag, c_values,\
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
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "No specials")

#repeat many times...
sa= SourceArticles(omit_stopwords=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Stopwords only")

sa= SourceArticles(stdize_article=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Stdize only")

sa= SourceArticles(stdize_kws=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "keywords only")

sa= SourceArticles(replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Synonyms only")

sa= SourceArticles(omit_stopwords=True, stdize_article=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Stopwords and stdize")


sa= SourceArticles(omit_stopwords=True, stdize_kws=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Stopwords and kws")

sa= SourceArticles(omit_stopwords=True, replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Stopwords and synonyms")



sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True, replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "everything")

sa= SourceArticles(stdize_article=True, stdize_kws=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "stdize and kws")

sa= SourceArticles(stdize_article=True, stdize_kws=True, replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "not stopwords")

sa= SourceArticles(stdize_article=True, replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Stdize and synonyms")

sa= SourceArticles(stdize_kws=True, replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "kws and synonyms")


sa= SourceArticles(omit_stopwords=True, stdize_kws = True, replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "not stdize")

sa= SourceArticles(omit_stopwords=True, stdize_article=True, replace_with_synonyms=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "not kws")

sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "not synonyms")

