from svm_utils import subsets, five_fold_validation_check_same_source, normalize
from article_group import ArticleGroup, create_strict_article_group_from_sa
from util import SourceArticles

thresholds= [0]
c_values= [.0001, .001, .001,]

sa= SourceArticles()
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "Something about test")

#repeat many times...
sa= SourceArticles(something=True)
ag= create_strict_article_group_from_sa(sa, 1000, 20)
get_results(ag, "about test")


def get_results(ag, label):
  accuracy, false_postives, false_negatives, c_value= find_best(ag, c_values,\
                                                                thresholds)
  print ""
  #print stuff here
  print ""
