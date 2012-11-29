from svm_utils import subsets, five_fold_validation_check_same_source,\
        normalize, find_best
from article_group import ArticleGroup, create_all_matching_keywords_article_group_from_sa
from util import SourceArticles

thresholds= [0]
c_values= [.001, .01, .1, 1, 5, 10]
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
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "No specials, keywords= " + keyword_list + ", article number\
                =" + str(i))


#repeat many times...
sa= SourceArticles(omit_stopwords=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "No stopwords, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(stdize_article=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "stdize only, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(stdize_kws=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "kws only, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "synonyms only, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(omit_stopwords=True, stdize_article=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "stopwords and stdize, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(omit_stopwords=True, stdize_kws=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "stopwords and kws, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(omit_stopwords=True, replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "stopwords and synonyms, keywords= " + keyword_list + ", article number\
                =" + str(i))



sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True, replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "everything, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(stdize_article=True, stdize_kws=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "stdize and kws, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(stdize_article=True, stdize_kws=True, replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "everything but stopwords, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(stdize_article=True, replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "stdize and synonyms, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(stdize_kws=True, replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "kws and synonyms, keywords= " + keyword_list + ", article number\
                =" + str(i))



sa= SourceArticles(omit_stopwords=True, stdize_kws = True, replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "without stdize, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(omit_stopwords=True, stdize_article=True, replace_with_synonyms=True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "without kws, keywords= " + keyword_list + ", article number\
                =" + str(i))


sa= SourceArticles(omit_stopwords=True, stdize_article=True, stdize_kws = True)
for i in xrange(sa.count):
  ag= create_all_matching_keywords_article_group_from_sa(sa, 1000, 200, i)
  if ag.count_sources > 8:
    keyword_list= ""
    for word in list(sa.get_keywords(i)):
      keyword_list+= " " + word

    get_results(ag, "without synonyms, keywords= " + keyword_list + ", article number\
                =" + str(i))


