import math, random
from util import SourceArticles, cosine, time_function
from hac import improved_hac
import time
import cPickle as pickle

MAX_ARTICLE_NUM = 2500

def log(x):
    if x <= 0:
        return float("-INF")
    return math.log(x)


class HMM_State():
    def __init__(self,
                 sgid_to_cid,
                 clusters,
                 cluster_counts,
                 transitions,
                 CHe,
                 Ne,
                 phrases):

        self.sgid_to_cid = sgid_to_cid
        self.clusters = clusters
        self.cluster_counts = cluster_counts
        self.transitions = transitions
        self.CHe = CHe
        self.Ne = Ne
        self.phrases = phrases


class HMM():

    def __init__(self,
                 ngram,
                 num_articles=None,
                 use_clusters=True,
                 use_pickled=True,
                 pickle_output=True,
                 pickle_filename="hmm.pickle"):
        self.ngram = ngram

        # Set up the source articles
        self.src_articles = SourceArticles(
            #stdizer=SourceArticles.PORTER_STEMMER,
            omit_stopwords=True,
            stdize_kws=True,
            stdize_article=True,
            max_phrase_size=ngram
        )

        if not num_articles:
            num_articles = self.src_articles.count

        start = time.time()

        if use_pickled:
            f = open(pickle_filename, 'rb')
            hmm_state = pickle.load(f)
            f.close()

            self.sgid_to_cid = hmm_state.sgid_to_cid
            self.clusters = hmm_state.clusters
            self.cluster_counts = hmm_state.cluster_counts
            self.transitions = hmm_state.transitions
            self.CHe = hmm_state.CHe
            self.Ne = hmm_state.Ne
            self.phrases = hmm_state.phrases

        else:
            self.build_hmm(num_articles, use_clusters)

        print "Building hmm took {0} seconds".format(time.time() - start)

        if pickle_output:
            hmm_state = HMM_State(self.sgid_to_cid,
                                  self.clusters,
                                  self.cluster_counts,
                                  self.transitions,
                                  self.CHe,
                                  self.Ne,
                                  self.phrases)
            f = open(pickle_filename, 'wb')
            pickle.dump(hmm_state, f)
            f.close()

    def build_hmm(self, num_articles, use_clusters):
        self.spin_groups = [frozenset()]  # List of spin groups (spin group is a set of phrase tuples), indexed by spin group ID
        self.spin_groups_inverse = {frozenset():0}  # Mapping from spin group to spin group ID
        self.phrases = {} # Set of all unique phrases


        article_num = random.randint(0, MAX_ARTICLE_NUM / 2) * 2
        used_articles = []

        # First pass through articles to get all unique spin groups
        for _ in range(num_articles):
            article_num = article_num + 2 % MAX_ARTICLE_NUM
            used_articles.append(article_num)

            for sentence in self.src_articles.get_article_sentences(article_num):
                for spin_group in sentence:
                    if spin_group not in self.spin_groups_inverse:
                        sgid = len(self.spin_groups)
                        self.spin_groups.append(spin_group)
                        self.spin_groups_inverse[spin_group] = sgid
                        # Map phrases in this spin group to this spin group ID
                        for phrase in spin_group:
                            if phrase not in self.phrases:
                                self.phrases[phrase] = []
                            self.phrases[phrase].append(sgid)
        if use_clusters:
            self.sgid_to_cid , self.clusters = improved_hac(self.spin_groups, self.spin_groups_inverse, self.phrases)
        else:
            self.sgid_to_cid = dict((x,x) for x in self.spin_groups_inverse.values())
            self.clusters = dict(enumerate(self.spin_groups))

        self.transitions = {}  # Mapping rom spin group ID to dict of spgid to counts
        self.cluster_counts = {0:0} # Mapping from spin group ID to number of occurances of that spin group

        # Second pass through articles to get transition probabilities
        for article_num in used_articles:
            for sentence in self.src_articles.get_article_sentences(article_num):
                prev_cid = None
                for spin_group in sentence:
                    sgid = self.spin_groups_inverse[spin_group]
                    cid = self.sgid_to_cid[sgid]

                    self.cluster_counts[cid] = self.cluster_counts.get(cid, 0) + 1

                    # Add the edge from prev_spgid to spgid
                    transition_from_prev = self.transitions.get(prev_cid, {})
                    transition_from_prev_to_cur = transition_from_prev.get(cid, 0)
                    transition_from_prev_to_cur += 1
                    transition_from_prev[cid] = transition_from_prev_to_cur
                    self.transitions[prev_cid] = transition_from_prev

                    prev_cid = cid

        # Store # of spin group occurances and # of unique spin groups
        self.CHe = sum(self.cluster_counts.values())
        self.Ne = len(self.cluster_counts)

    def transition_prob(self, src_cid, dest_cid):
        '''
        Returns probability that src_cid will transition to dest_cid.
        Uses Witten-Bell smoothing:
            http://www.ee.columbia.edu/~stanchen/e6884/labs/lab3/x207.html
        '''
        edges_from_src = self.transitions.get(src_cid, {})
        # "unknown" state transitions to all others
        if src_cid == 0:
            edges_from_src = self.cluster_counts

        # number of times dest_cid occurs
        Cd = float(self.cluster_counts.get(dest_cid, 0))

        # count of transitions from src_cid to dest_cid
        Csd = float(edges_from_src.get(dest_cid, 0))

        # number of total transitions from src_cid
        CHs = float(sum(edges_from_src.values()))
        # numver of unique transitions from src_cid
        Ns = float(len(edges_from_src))

        # No transitions from src_cid, return 0
        if CHs == 0.0:
            return 0.0

        Pmle = Csd / CHs
        Pb = (Cd + 1) / (self.CHe + self.Ne)

        return ((CHs / (CHs + Ns)) * Pmle) + ((Ns / (CHs + Ns)) * Pb)
        #return Pmle

    def emission_prob(self, cid, phrase):
        '''
        Returns probability that sgid will emit phrase. Phrase is a list of strings.
        '''
        # Unknown state can only emit unknown single word phrases
        if cid == 0:
            if len(phrase) == 1 and phrase not in self.phrases:
                return 1.0
            return 0.0

        cluster = self.clusters[cid]
        if phrase in cluster:
            return 1.0 / len(cluster)
        else:
            return 0.0


    def classify_sentence(self, sentence):
        '''
        Returns the most likely sequence of spin groups that could have generated sentence
        n is the number of n-grams to consider
        '''
        deltas = []

        for t in range(len(sentence)):
            delta = {}
            for cid in self.clusters:
                for wb in range(self.ngram):
                    key = (cid, wb)

                    # Make sure theres enough words back
                    if t-wb < 0:
                        delta[key] = (float("-INF"), (None, 0))
                        continue

                    # Extract the phrase
                    phrase = sentence[t-wb:t+1]

                    # Is a start probability
                    if t-1-wb < 0:
                        value = log(self.transition_prob(None, cid)) + log(self.emission_prob(cid, phrase))
                        delta[key] = (value , (None, 0))

                    # Not a start probability
                    else:
                        prev_delta = deltas[t-1-wb]
                        best_prev_key = None
                        max = None
                        emit_prob = self.emission_prob(cid, phrase)
                        if (emit_prob > 0.0):
                            for (prev_cid, prev_wb), (prev_prob, prev_key) in prev_delta.iteritems():
                                value = prev_prob + log(self.transition_prob(prev_cid, cid)) + log(emit_prob)
                                if value > max:
                                    max = value
                                    best_prev_key = (prev_cid, prev_wb)
                        if best_prev_key:
                            delta[key] = (max , best_prev_key)

            deltas.append(delta)

        # Find the max in the last delta
        last_delta = deltas[t]
        max_prob = None
        best_kv = None
        for (cid, wb) , (prob, prev_key) in last_delta.iteritems():
            if prob >= max_prob:
                max_prob = prob
                best_kv = (cid, wb) , (prob, prev_key)

        # Backtrack
        sgs = []
        t = len(sentence)-1
        while t >= 0:
            (cid, wb) , (_, prev_key) = best_kv
            sgs.append(cid)
            t = t - wb - 1
            best_kv = prev_key , deltas[t].get(prev_key, (float("-INF"), (None, 0)))

        # Returns the spin groups found
        sgs.reverse()
        return sgs


    def classify_article(self, article):
        '''
        article is list of sentence strings.
        returns list of sentences corresponding to
        '''
        spin_groups = []
        for sentence in article:
            classified = self.classify_sentence(tuple(sentence.split()))
            spin_groups = spin_groups + classified
        return spin_groups

    def classify_article_formatted(self, article):
        classified_article_groups = hmm.classify_article(article)

        classified_article = []
        for group in classified_article_groups:
            cluster = hmm.clusters[group]
            for phrase in cluster:
                for word in phrase:
                    classified_article.append(word)
            #print "ID: {0}\t{1}".format(group, cluster)
        article = " ".join(article).split()

        return (article , classified_article)

    def print_comparison_stats(self, article1, article2, classified_article1, classified_article2):
        print "COSINE OF ARTICLES: {0}".format(cosine(" ".join(article1), " ".join(article2)))
        print "COSINE OF CLASSIFIED ARTICLES: {0}".format(cosine(" ".join(classified_article1), " ".join(classified_article2)))
        print "cosine of A1 and classified A1: {0}".format(cosine(" ".join(classified_article1), " ".join(article1)))
        print "cosine of A2 and classified A2: {0}".format(cosine(" ".join(classified_article2), " ".join(article2)))
        print "cosine of A1 and classified A2: {0}".format(cosine(" ".join(classified_article2), " ".join(article1)))
        print "cosine of A2 and classified A1: {0}".format(cosine(" ".join(classified_article1), " ".join(article2)))
        print "WORDS IN COMMON A1 and classified A1: {0}".format(float(len(set(article1).intersection(set(classified_article1)))) / len(set(article1)))
        print "WORDS IN COMMON A2 and classified A2: {0}".format(float(len(set(article2).intersection(set(classified_article2)))) / len(set(article2)))
        print "WORDS IN COMMON A1 and classified A2: {0}".format(float(len(set(article1).intersection(set(classified_article2)))) / len(set(article1)))
        print "WORDS IN COMMON A2 and classified A1: {0}".format(float(len(set(article2).intersection(set(classified_article1)))) / len(set(article2)))

    def compare_articles(self, article1, article2):
        '''
        articles are list of sentence strings
        '''
        (article1 , classified_article1) = self.classify_article_formatted(article1)
        (article2 , classified_article2) = self.classify_article_formatted(article2)
        self.print_comparison_stats(article1, article2, classified_article1, classified_article2)



if __name__ == "__main__":
    use_pickled = False
    pickle_output = False
    pickle_filename = "hmm-600-clustered.pickle"

    num_articles = 50
    article_num = random.choice(range(num_articles,2959))
    sentence_num = 0

    hmm = HMM(4,
             num_articles,
             use_clusters=True,
             use_pickled=False,
             pickle_output=True,
             pickle_filename="hmm-600-clustered.pickle",
             )

    #TODO: look at 202 sentence 1
    articles_a = hmm.src_articles.spin_dissimilar_articles(random.choice(range(num_articles,2900)), 2)
    articles_b = hmm.src_articles.spin_dissimilar_articles(random.choice(range(num_articles,2900)), 2)

    (article_a0 , classified_article_a0) = hmm.classify_article_formatted(articles_a[0])
    (article_a1 , classified_article_a1) = hmm.classify_article_formatted(articles_a[1])

    #(article_b0 , classified_article_b0) = hmm.classify_article_formatted(articles_b[0])
    #(article_b1 , classified_article_b1) = hmm.classify_article_formatted(articles_b[1])


    print "--------------------------------------------------------------------"
    print "--------------------------------------------------------------------"

    print "SIMILAR ARTICLES A:\n"
    hmm.print_comparison_stats(article_a0, article_a1, classified_article_a0, classified_article_a1)
    print
    '''
    print "SIMILAR ARTICLES B:\n"
    hmm.print_comparison_stats(article_b0, article_b1, classified_article_b0, classified_article_b1)

    print "--------------------------------------------------------------------"

    print "NOT SIMILAR ARTICLES A0 B0:\n"
    hmm.print_comparison_stats(article_a0, article_b0, classified_article_a0, classified_article_b0)
    print
    print "NOT SIMILAR ARTICLES A1 B0:\n"
    hmm.print_comparison_stats(article_a1, article_b0, classified_article_a1, classified_article_b0)
    print
    print "NOT SIMILAR ARTICLES A0 B1:\n"
    hmm.print_comparison_stats(article_a0, article_b1, classified_article_a0, classified_article_b1)
    print
    print "NOT SIMILAR ARTICLES A1 B1:\n"
    hmm.print_comparison_stats(article_a1, article_b1, classified_article_a1, classified_article_b1)
    '''
