from svm_utils import subsets, five_fold_validation_check_same_source, normalize
from article_group import ArticleGroup, create_strict_article_group_from_sa
from util import SourceArticles

thresholds= [0]
c_values= [.125]

sa= SourceArticles()
ag= create_strict_article_group_from_sa(sa, 1000, 20)

#normalized_examples= normalize(ag.svm_ready_examples)
train_sets, validate_sets= subsets(ag.svm_ready_examples, 5)

print "validate size= " + str(len(validate_sets[0]))
print "train size= " + str(len(train_sets[0]))

for c_value in c_values:
    print five_fold_validation_check_same_source(train_sets, validate_sets,\
                                                 c_value, thresholds)
