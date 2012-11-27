from util import SourceArticles, cosine
import random


NUM_POSITIVES = NUM_NEGATIVES = 100
THRESHOLDS = [x / 100.0 for x in xrange(0, 105, 5)]


def get_cosines(src_articles):
    positive_cosines = []
    negative_cosines = []

    while len(positive_cosines) < NUM_POSITIVES:
        num = random.randint(0, src_articles.count - 1)
        a1, a2 = src_articles.spin_dissimilar_articles(num, 2)
        positive_cosines.append(cosine(" ".join(a1), " ".join(a2)))

    while len(negative_cosines) < NUM_NEGATIVES:
        num1 = random.randint(0, src_articles.count - 1)
        similar_articles = list(src_articles.get_very_similar_articles(num1))
        if not similar_articles:
            continue
        num2 = random.choice(similar_articles)
        a1 = " ".join(src_articles.spin_article(num1))
        a2 = " ".join(src_articles.spin_article(num2))
        negative_cosines.append(cosine(a1, a2))

    return positive_cosines, negative_cosines


def calculate_tp_fp(positive_cosines, negative_cosines, threshold):
    tp, fp = 0.0, 0.0

    for cos in positive_cosines:
        if cos >= threshold:
            tp += 1

    for cos in negative_cosines:
        if cos >= threshold:
            fp += 1

    return tp / NUM_POSITIVES, fp / NUM_NEGATIVES


def baseline_roc():
    src_articles = SourceArticles(
            stdize_kws=True,
            stdize_article=False,
            stdizer=SourceArticles.PORTER_STEMMER,
            omit_stopwords=False,
            max_phrase_size=None
        )

    positive_cosines, negative_cosines = get_cosines(src_articles)

    for threshold in THRESHOLDS:
        tp_rate, fp_rate = calculate_tp_fp(positive_cosines, negative_cosines, threshold)
        print "{threshold}\n\tTP RATE : {tp_rate}\n\tFP RATE : {fp_rate}".format(**locals())


if __name__ == "__main__":
    baseline_roc()
