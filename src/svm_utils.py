from article_group import ArticleGroup
import math
import random
import svmlight

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
    chunk_size= len(train) / folds
    chunks= [train[i:i+chunk_size] for i in range(0, len(train), chunk_size)]

    for i in range(len(chunks)):
        validate_sets.append(chunks[i])
        temp= [];
        for j in range(len(chunks)):
            if i != j:
                temp+= chunks[j]

        train_sets.append(temp)

    return train_sets, validate_sets

def create_classifications(models, test_set):
    '''
    For each supplied model, use svm light to classify the 
    test_set with that model
    '''
    classifications= {}
    for m in models.keys():
        classifications[m]= svmlight.classify(models[m], test_set)

    return classifications

def five_fold_validation_check_same_source(training_sets, validation_sets,\
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

            predictions= predictions_from_classifications(classifications, threshold)

            true_classifications= []
            for ex in validation_sets[i]:
                true_classifications.append(ex[0])

            predicted_sim_pairs= create_similarity_pairs(predictions)
            actual_sim_pairs= create_similarity_pairs(true_classifications)

            accuracy= find_accuracy(actual_sim_pairs, predicted_sim_pairs)
            print "accuracy for threshold " + str(threshold) + "= " +\
            str(accuracy)

            if accuracy[0] > best_accuracy:
                best_accuracy= accuracy[0]

        total_accuracy += best_accuracy

    return total_accuracy/len(training_sets)

def create_similarity_pairs(predictions):
    '''
    Outputs a sequence of binary classifications generated by
    pairing the examples of the together.  1 indicates that 
    they have the same source, and -1 indicates that they do not.
    Note: Ordering is quite important for other functions
    '''
    sim_pairs= []
    for c1 in predictions:
        for c2 in predictions:
            if c1 is None or c2 is None:
                sim_pairs.append(-1)
            else:
                if c1 == c2:
                    sim_pairs.append(1)
                else:
                    sim_pairs.append(-1)

    return sim_pairs

def predictions_from_classifications(classifications, threshold):
    '''
    Find the class that each example is most likely to have come from.
    Returns the class name and the strength of the classification.
    If the strength of the classification is below the threshold,
    classify as 'None'
    '''
    predictions= []

    num_examples= 0
    #this is bad, but I don't really know python that well lol
    num_examples= len(classifications[classifications.keys()[0]])
    print "pfc num examples= "+ str(num_examples)

    for example in xrange(num_examples):
        best_value= 0
        best_index= None
        for classification_index in classifications.keys():
            if classifications[classification_index][example] > best_value:
                best_value= classifications[classification_index][example]
                best_index= classification_index

        print best_value
        if best_value < threshold:
            best_index= None

        predictions.append((best_index, best_value))

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
        div= math.sqrt(reduce(lambda x, y: x+y[1]**2, features, 0))
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
        if classifications[i] == 1:
            if real_classes[i] == 1:
                true_plus += 1
            else:
                false_plus += 1
        else:
            if real_classes[i] == -1:
                true_minus += 1
            else:
                false_minus += 1

    accuracy= (true_plus+true_minus)/len(real_classes)
    return (accuracy, false_plus, false_minus)
