'''
Created on Nov 12, 2012

@author: Will
'''

from util import SourceArticles, cosine, gen_phrases
import random

source_articles = SourceArticles()

def baseline_average_cos(article_num, num_times, print_out=True, equal_prob=True):
    '''
    Generates two random actual articles of source article article_num
    Computes the cosine similarity
    Does this num_times and outputs the lowest cos, highest, and average
    '''
    lowest = float("inf")
    highest = float("-inf")
    total = 0.0
    for _ in xrange(num_times):
        if equal_prob:
            a1 = source_articles.spin_articles(article_num)[0]
            a2 = source_articles.spin_articles(article_num)[0]
        else:
            a1, a2 = source_articles.spin_articles(article_num, 2)

        cos_sim = cosine(a1, a2)
        lowest = min(lowest, cos_sim)
        highest = max(highest, cos_sim)
        total += cos_sim

    average = total / num_times
    if print_out:
        print 'Ran {0} times for article {1}'.format(num_times, article_num)
        if equal_prob: print 'Generated with equal probability'
        else: print 'Generated using heuristic to produce low cosine'
        print 'Lowest : {0}\nHighest : {1}\nAverage : {2}\n'.format(lowest, highest, average)

    return lowest, highest, average

def baseline_average_cos_all(num_times, num_articles=source_articles.count, equal_prob=True):
    '''
    Does baseline_average_cos for every article for num_times 
    each. 
    '''
    lowest_overall = float("inf")
    highest_overall = float("-inf")
    # Lowest/highest average along with what article num had that average
    lowest_average = (float("inf"), -1)
    highest_average = (float("-inf"), -1)
    total = 0.0
    num_under_threshold = 0
    threshold = .32

    for article_num in xrange(source_articles.count):
        if article_num / 250 * 250 == article_num:
            print article_num
        lowest_for_this, highest_for_this, average_for_this = baseline_average_cos(article_num, num_times, print_out=False, equal_prob=equal_prob)
        lowest_overall = min(lowest_overall, lowest_for_this)
        highest_overall = max(highest_overall, highest_for_this)

        if average_for_this > .9:
            print "WARNING : average for article num {0}, id {1}, was {2}".format(article_num, source_articles.get_id(article_num), average_for_this)
        if average_for_this < lowest_average[0]:
            lowest_average = (average_for_this, article_num)

        if average_for_this > highest_average[0]:
            highest_average = (average_for_this, article_num)

        total += average_for_this
        if average_for_this < threshold:
            num_under_threshold += 1

    average = total / source_articles.count

    print "Ran {0} times for all {1} articles".format(num_times, source_articles.count)
    if equal_prob: print 'Generated with equal probability'
    else: print 'Generated using heuristic to produce low cosine'
    print "Lowest overall : {0}\nHighest overall : {1}".format(lowest_overall, highest_overall)
    print "Lowest average : {0}, {1}\nHighest average : {2} , {3}".format(lowest_average[0], lowest_average[1], highest_average[0], highest_average[1])
    print "Average : {0}".format(average)
    print "Number of source articles with average under {0} : {1}".format(threshold, num_under_threshold)

def baseline_cos_different_articles(a1_num, a2_num, num_times):
    lowest = float("inf")
    highest = float("-inf")
    total = 0.0
    for _ in xrange(num_times):
        a1 = source_articles.spin_articles(a1_num)[0]
        a2 = source_articles.spin_articles(a2_num)[0]
        cos_sim = cosine(a1, a2)
        lowest = min(lowest, cos_sim)
        highest = max(highest, cos_sim)
        total += cos_sim

    average = total / num_times
    return lowest, highest, average


def baseline_cos_different(num_pairs, num_times):

    '''
    How similar are articles created from different source articles?
    for num_pairs
        Take two random source articles
        for num_times
            generate a random article from each source
            calculate cosine
        record average cosine
    '''

    lowest_overall = float("inf")
    highest_overall = float("-inf")
    # Lowest/highest average along with what article num had that average
    lowest_average = float("inf")
    highest_average = float("-inf")
    total = 0.0

    for _ in xrange(num_pairs):
        a1_num = random.randint(0, source_articles.count - 1)
        a2_num = a1_num
        while a2_num == a1_num:
            a2_num = random.randint(0, source_articles.count - 1)

        lowest, highest, average = baseline_cos_different_articles(a1_num, a2_num, num_times)

        lowest_overall = min(lowest_overall, lowest)
        highest_overall = max(highest_overall, highest)
        lowest_average = min(lowest_average, average)
        highest_average = max(highest_average, average)
        total += average

    average = total / num_pairs
    print "Calculated cosine of {0} pairs of random articles for {1} pairs of random source articles".format(num_times, num_pairs)
    print "Lowest overall similarity : {0}".format(lowest_overall)
    print "Highest overall similarity : {0}".format(lowest_overall)
    print "Lowest average : {0}".format(lowest_average)
    print "Highest average : {0}".format(highest_average)
    print "Average average : {0}".format(average)


def get_stats_all():
    total_spin_groups = 0.0
    total_elements = 0.0
    for article_num in xrange(source_articles.count):
        num_spin_groups, num_elements, _ = source_articles.get_stats(article_num)
        total_spin_groups += num_spin_groups
        total_elements += num_elements

    average_groups = total_spin_groups / source_articles.count
    average_elements = total_elements / total_spin_groups

    print "Average number of spin groups : {0}".format(average_groups)
    print "Average elements per spin group : {0}".format(average_elements)

def baseline_cosine_keywords(num_times):
    '''
    Essentially the same thing as cosine_different.
    However for pairs, we only use pairs which have the same
    keywords. 
    '''
    num_articles = source_articles.count
    num_pairs = 0
    lowest_overall = float("inf")
    highest_overall = float("-inf")
    # Lowest/highest average along with what article num had that average
    lowest_average = float("inf")
    highest_average = float("-inf")
    total = 0.0
    for a1_num in xrange(num_articles - 1):
        a1_keywords = source_articles.get_keywords(a1_num)
        a2_num = -1
        for num in xrange(a1_num + 1, num_articles):
            if a1_keywords == source_articles.get_keywords(num):
                a2_num = num
                break
        else:
            # No articles with same keywords
            continue
        num_pairs += 1
        lowest, highest, average = baseline_cos_different_articles(a1_num, a2_num, num_times)

        lowest_overall = min(lowest_overall, lowest)
        highest_overall = max(highest_overall, highest)
        lowest_average = min(lowest_average, average)
        highest_average = max(highest_average, average)
        total += average

    average = total / num_pairs
    print "Calculated cosine of {0} pairs of random articles for {1} pairs of source articles with same keywords".format(num_times, num_pairs)
    print "Lowest overall similarity : {0}".format(lowest_overall)
    print "Highest overall similarity : {0}".format(highest_overall)
    print "Lowest average : {0}".format(lowest_average)
    print "Highest average : {0}".format(highest_average)
    print "Average average : {0}".format(average)





#baseline_cosine_keywords(100)
baseline_average_cos_all(25, equal_prob=False)

#baseline_cos_different(1000, 100)

