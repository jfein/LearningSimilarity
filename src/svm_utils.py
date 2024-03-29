from article_group import ArticleGroup
import math
import random
import svmlight
import os

pairs_to_look_at= None

def change_to_binary_examples(training_data, target_example):
    '''
    Changes the example labels in place such that all examples
    of the target class are now labeled '1' and all other 
    examples are labeled '-1'
    '''
    binary= []
    for i in range(len(training_data)):
        if training_data[i][0] == target_example:
            binary.append((1, training_data[i][1]))
        else:
            binary.append((-1, training_data[i][1]))

    return binary

def subsets(train, folds):
    '''
    Splits the train data into pairs of training and validation
    sets.  The number of pairs is equal to folds.  In each pair,
    the number of examples in the training set is
    (folds-1)/(folds) * len(train)
    '''
    random.shuffle(train)

    train_sets= []
    validate_sets= []

    #size of test_set arbitrarily set to 30% of input
    test_set= train[0: int(.3*len(train))]
    remainder= train[int(.3*len(train)):len(train)]

    chunk_size= len(remainder) / folds
    chunks= [remainder[i:i+chunk_size] for i in range(0, len(remainder), chunk_size)]

    for i in range(len(chunks)):
        validate_sets.append(chunks[i])
        temp= [];
        for j in range(len(chunks)):
            if i != j:
                temp+= chunks[j]

        train_sets.append(temp)

    return train_sets, validate_sets, test_set

def create_classifications(models, test_set):
    '''
    For each supplied model, use svm light to classify the 
    test_set with that model
    '''
    classifications= {}
    for m in models.keys():
        classifications[m]= svmlight.classify(models[m], test_set)

    return classifications

def find_best(c_values, threshold, train_sets, validation_sets, test_set):
    best_c_value= 0
    best_acc= 0

    #find the best c value through brute force
    for c in c_values:
        acc= five_fold_validation_check_same_source(train_sets, validation_sets,\
                                                   c, threshold)
        if acc > best_acc:
            best_acc= acc
            best_c_value= c

    #now combine the validation and traning data
    true_training= validation_sets[0]+train_sets[0]

    #retrain the model, try the models on the test set and report results
    models= find_models(true_training, best_c_value)
    classifications= create_classifications(models, test_set)
    accuracy, true_plus, true_minus, false_plus, false_minus= get_accuracy_for_same_source\
            (classifications, threshold, test_set)

    #write out the articles used so they can be part of the cosine baseline
    if not os.path.exists('positives.ex'):
        positives_file = open('positives.ex', 'w')
        negatives_file = open('negatives.ex', 'w')

        for ex in pairs_to_look_at:
            ex0= convert_bag_of_words_to_numbers(test_set[ex[0]][1])
            ex1= convert_bag_of_words_to_numbers(test_set[ex[1]][1])
            if ex[2] == 1:
                positives_file.write(ex0)
                positives_file.write(ex1)
            else:
                negatives_file.write(ex0)
                negatives_file.write(ex1)

        positives_file.close()
        negatives_file.close()

    return accuracy, true_plus, true_minus, false_plus, false_minus, best_c_value

def convert_bag_of_words_to_numbers(bag):
    result= ""
    for tup in bag:
        for _ in xrange(int(tup[1])):
            result += str(tup[0]) + " "

    result += "\n"
    return result

def get_accuracy_for_same_source(classifications, threshold, test_data):
    predictions= predictions_from_classifications(classifications, threshold)

    true_classifications= []
    for ex in test_data:
        true_classifications.append(ex[0])

    #hardcoding 500 for ROC graph
    actual_sim_pairs= create_similarity_pairs(true_classifications, 500)
    predicted_sim_pairs= create_particular_similarity_pairs(predictions)

    return find_accuracy(actual_sim_pairs, predicted_sim_pairs)

def five_fold_validation_check_same_source(training_sets, validation_sets,\
                                          c_value, threshold):
    '''
    Performs five fold validation using the supplied training and validation
    sets.  Tries each value in thresholds and uses whichever gives the best
    result. Returns the average accuracy across all training sets
    '''
    total_accuracy= 0.0
    for i in xrange(len(training_sets)):
        models= find_models(training_sets[i], c_value)
        classifications= create_classifications(models, validation_sets[i])

        best_accuracy= 0.0

        accuracy= get_accuracy_for_same_source(classifications, threshold,
                                               validation_sets[i])
        #print "accuracy for threshold " + str(threshold) + "= " +\
        #        str(accuracy)

        if accuracy[0] > best_accuracy:
            best_accuracy= accuracy[0]

        total_accuracy += best_accuracy

    return total_accuracy/len(training_sets)

def create_similarity_pairs(predictions, num_ex):
    '''
    Outputs a sequence of binary classifications generated by
    pairing the examples of the together.  1 indicates that 
    they have the same source, and -1 indicates that they do not.
    Also outputs the specific pairings used
    Note: Ordering is quite important for other functions
    '''
    global pairs_to_look_at

    if pairs_to_look_at is None:
        pos_pairs = []
        neg_pairs = []
        for i in range(len(predictions)):
            for j in range(len(predictions)):
                c1= predictions[i]
                c2= predictions[j]
                if c1 is None or c2 is None:
                    neg_pairs.append((i,j,-1))
                else:
                    if c1 == c2:
                        pos_pairs.append((i,j,1))
                    else:
                        neg_pairs.append((i,j,-1))

        random.shuffle(pos_pairs)
        random.shuffle(neg_pairs)

        sim_pairs= []

        if num_ex > len(pos_pairs):
            num_ex= len(pos_pairs)

        if num_ex > len(neg_pairs):
            num_ex= len(neg_pairs)

        for i in range(num_ex):
            sim_pairs.append(pos_pairs[i])
            sim_pairs.append(neg_pairs[i])

        print "new global pairs_to_look_at"
        pairs_to_look_at= sim_pairs
        return sim_pairs
    else:
        return create_particular_similarity_pairs(predictions)

def create_particular_similarity_pairs(predictions):
    '''
    Outputs a sequence of binary classifications generated by
    pairing the examples of the together.  1 indicates that 
    they have the same source, and -1 indicates that they do not.
    Note: Ordering is quite important for other functions
    '''
    sim_pairs= []
    for tup in pairs_to_look_at:
        i= tup[0]
        j= tup[1]
        c1= predictions[i]
        c2= predictions[j]
        if c1 is None or c2 is None:
            sim_pairs.append((i,j,-1))
        else:
            if c1 == c2:
                sim_pairs.append((i,j,1))
            else:
                sim_pairs.append((i,j,-1))

    return sim_pairs

def predictions_from_classifications(classifications, threshold):
    '''
    Find the class that each example is most likely to have come from.
    Returns the class name and the strength of the classification.
    If the strength of the classification is below the threshold,
    classify as 'None'
    '''
    predictions= []

    #this is bad, but I don't really know python that well lol
    num_examples= len(classifications[classifications.keys()[0]])

    for example in xrange(num_examples):
        best_value= 0
        best_index= None
        for classification_index in classifications.keys():
            if classifications[classification_index][example] > best_value:
                best_value= classifications[classification_index][example]
                best_index= classification_index

        if best_value < threshold:
            best_index= None

        predictions.append(best_index)

    return predictions

def find_models(examples, c_value):
    '''
    For each class of example article, create a model.  These models will be used to
    determine the liklihood that a test example comes from each class's source.
    '''
    models= {}
    learned_classes= {}
    for example in examples:
        class_num = example[0]
        if class_num not in learned_classes:
            #print class_num
            train= change_to_binary_examples(examples, class_num)
            models[class_num]= svmlight.learn(train, type='classification', C=c_value)
            learned_classes[class_num] = 1

    return models

def normalize(examples):
    '''
    normalize the feature vectors of all examples
    so that they sum to one
    '''
    normalized_examples= []
    for ex in examples:
        features= ex[1]
        div= math.sqrt(reduce(lambda x, y: x+y[1]**2, features, 0.0))
        normalized_features= []
        for feat in features:
            normalized_features.append((feat[0], feat[1]/div))

        normalized_examples.append((ex[0],normalized_features))

    print str(math.sqrt(reduce(lambda x, y: x+y[1]**2, 
                    normalized_examples[0][1], 0)))
    return normalized_examples

def find_accuracy(real_classes, classifications):
    '''
    Finds the accuracy, false positives, and false negatives.
    The inputs are arrays of -1 and 1.  Each index in the arrays
    corresponds to the same example.
    '''

    true_plus= 0.0
    false_plus= 0.0
    true_minus= 0.0
    false_minus= 0.0

    for i in xrange(len(real_classes)):
        #print "length of reals= "+ str(len(real_classes))
        #print "length of classifications= "+ str(len(classifications))
        #print classifications
        if classifications[i][2] == 1:
            if real_classes[i][2] == 1:
                true_plus += 1
            else:
                false_plus += 1
        else:
            if real_classes[i][2] == -1:
                true_minus += 1
            else:
                false_minus += 1

    accuracy= (true_plus+true_minus)/len(real_classes)
    return (accuracy, true_plus, true_minus, false_plus, false_minus)

def concatenated_pairs(examples):
    concatenated_ps= []
    for ex in examples:
        for other_ex in examples:
            #hack to reduce number of examples
            #if random.randrange(100) != 0:
            #    continue

            class_label = -1
            if ex[0]  == other_ex[0]:
                class_label= 1

            new_example= (class_label, [])

            #merge the examples
            feat1= ex[1]
            feat2= other_ex[1]
            feat2_pos= 0
            for feat1_pos in xrange(len(feat1)):
                #insert features from feat2
                while feat2_pos < len(feat2) and feat2[feat2_pos][0] < feat1[feat1_pos][0]:
                    new_example[1].append(feat2[feat2_pos])
                    feat2_pos += 1

                #concatenate identical features
                if feat2_pos < len(feat2) and feat2[feat2_pos][0] == feat1[feat1_pos][0]:
                    new_example[1].append((feat2[feat2_pos][0],\
                                           feat1[feat1_pos][1]\
                                           + feat2[feat2_pos][1]))
                #add feature from feat1
                else:
                    new_example[1].append(feat1[feat1_pos])

            #append remaining features from 2
            while feat2_pos < len(feat2):
                new_example[1].append(feat2[feat2_pos])
                feat2_pos += 1

            concatenated_ps.append(new_example)

    return concatenated_ps


def find_best_pair_test(ag, c_values, thresholds):
    for threshold in thresholds:
        best_c_value= 0
        best_acc= 0
        concatenate_ps= concatenated_pairs(ag.svm_ready_examples)
        train_sets, validation_sets, test_set= subsets(concatenate_ps, 5)

        #find the best c value through brute force
        for c in c_values:
            acc= five_fold_validation_check_pair_test(train_sets, validation_sets,\
                                                       c, [threshold])
            if acc > best_acc:
                best_acc= acc
                best_c_value= c

        #now combine the validation and traning data
        true_training= validation_sets[0]+train_sets[0]

        #retrain the model, try the models on the test set and report results
        models= find_models(true_training, best_c_value)
        classifications= create_classifications(models, test_set)
        accuracy, false_plus, false_minus= get_accuracy_for_pair_test\
                (classifications, threshold, test_set)

        return accuracy, false_plus, false_minus, best_c_value

def get_accuracy_for_pair_test(classifications, threshold, test_data):
    predictions= predictions_from_classifications(classifications, threshold)

    #print "predictions= " + str(predictions)

    true_labels= []
    for ex in test_data:
        true_labels.append(ex[0])

    return find_accuracy(true_labels, predictions)

def five_fold_validation_check_pair_test(training_sets, validation_sets,\
                                          c_value, thresholds):
    '''
    Performs five fold validation using the supplied training and validation
    sets.  Tries each value in thresholds and uses whichever gives the best
    result. Returns the average accuracy across all training sets
    '''
    total_accuracy= 0.0
    for i in xrange(len(training_sets)):
        models= find_models(training_sets[i], c_value)
        classifications= create_classifications(models, validation_sets[i])

        #try the various thresholds and use whichever works best
        best_accuracy= 0.0
        for threshold in thresholds:

            accuracy= get_accuracy_for_pair_test(classifications, threshold,
                                                   validation_sets[i])
            print "accuracy for threshold " + str(threshold) + "= " +\
            str(accuracy)

            if accuracy[0] > best_accuracy:
                best_accuracy= accuracy[0]

        total_accuracy += best_accuracy

    return total_accuracy/len(training_sets)
