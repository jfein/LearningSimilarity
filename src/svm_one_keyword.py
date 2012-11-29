from svm_utils import subsets, five_fold_validation_check_same_source,\
        normalize, find_best
from article_group import ArticleGroup, create_keyword_article_group_from_sa
from util import SourceArticles

thresholds= [0]
c_values= [.001, .01, .1, 1, 5, 10]
keywords_to_use= list(SourceArticles().get_all_keywords())

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

def try_each(label):
    for kw in keywords_to_use:
        ag= create_keyword_article_group_from_sa(sa, 1000, 200, kw)
        if ag.count_sources > 3:
            get_results(ag, label+ " with keyword: " + kw)


sa= SourceArticles()
try_each("No specials")

#repeat many times...
sa= SourceArticles(omit_stopwords=True)
try_each("Stopwords only")

sa= SourceArticles(stdize_article=True)
try_each("Stdize only")

sa= SourceArticles(stdize_kws=True)
try_each("keywords only")

sa= SourceArticles(replace_with_synonyms=True)
try_each("Synonyms only")

sa= SourceArticles(omit_stopwords=True, stdize_article=True)
try_each("Stopwords and stdize")


sa= SourceArticles(omit_stopwords=True, stdize_kws=True)
try_each("Stopwords and kws")

sa= SourceArticles(omit_stopwords=True, replace_with_synonyms=True)
try_each("Stopwords and synonyms")



sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True, replace_with_synonyms=True)
try_each("everything")

sa= SourceArticles(stdize_article=True, stdize_kws=True)
try_each("stdize and kws")

sa= SourceArticles(stdize_article=True, stdize_kws=True, replace_with_synonyms=True)
try_each("not stopwords")

sa= SourceArticles(stdize_article=True, replace_with_synonyms=True)
try_each("Stdize and synonyms")

sa= SourceArticles(stdize_kws=True, replace_with_synonyms=True)
try_each("kws and synonyms")


sa= SourceArticles(omit_stopwords=True, stdize_kws = True, replace_with_synonyms=True)
try_each("not stdize")

sa= SourceArticles(omit_stopwords=True, stdize_article=True, replace_with_synonyms=True)
try_each("not kws")

sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True)
try_each("not synonyms")
