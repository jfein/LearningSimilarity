import math
from util import SourceArticles, cosine, time_function
from hac import improved_hac


def log(x):
    if x <= 0:
        return float("-INF")
    return math.log(x)
    

class HMM():

    def __init__(self, ngram, num_articles=None, use_clusters=True):
        self.ngram = ngram

        # Set up the source articles
        self.src_articles = SourceArticles(
            stdizer=SourceArticles.PORTER_STEMMER,
            omit_stopwords=True,
            stdize_kws=True,
            stdize_article=True,
            max_phrase_size=ngram
        )
        
        if not num_articles:
            num_articles = self.src_articles.count
        
        self.spin_groups = [frozenset()]  # List of spin groups (spin group is a set of phrase tuples), indexed by spin group ID
        self.spin_groups_inverse = {frozenset():0}  # Mapping from spin group to spin group ID
        self.phrases = {} # Set of all unique phrases
        
        # First pass through articles to get all unique spin groups
        for article_num in range(num_articles):
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
        for article_num in range(num_articles):
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
            
    @time_function
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
        
            

        
if __name__ == "__main__":
    num_articles = 200
    article_num = 324
    sentence_num = 0
    
    hmm = HMM(4, num_articles)
    
    print "ORIGINAL SENTENCE:"
    print hmm.src_articles.get_article_sentences(article_num)[sentence_num]
    
    #TODO: look at 202 sentence 1
    articles = hmm.src_articles.spin_dissimilar_articles(article_num, 2)
    #articles[1] = hmm.src_articles.spin_article(article_num+1)
    
    print "--------------------------------------------------------------------" 
    print "--------------------------------------------------------------------" 
    
    print "WITH CLUSTERING"
    
    sentence1 = tuple(articles[0][sentence_num].split())
    print len(sentence1)
    print "CLASSIFYING :\n{0}".format(sentence1)
    
    classified_sentence1 = set()
    groups = hmm.classify_sentence(sentence1)
    for group in groups:
        cluster = hmm.clusters[group]
        for phrase in cluster:
            for word in phrase:
                classified_sentence1.add(word)
        print "ID: {0}\t{1}".format(group, cluster)
        
    print "----------------------------------------------------------"  
    
    sentence2 = tuple(articles[1][sentence_num].split())
    print len(sentence2)
    print "CLASSIFYING :\n{0}".format(sentence2)
    
    classified_sentence2 = set()
    groups = hmm.classify_sentence(sentence2)
    for group in groups:
        cluster = hmm.clusters[group]
        for phrase in cluster:
            for word in phrase:
                classified_sentence2.add(word)
        print "ID: {0}\t{1}".format(group, cluster)
        
    print "----------------------------------------------------------"  
    
    print "COSINE OF SENTENCES: {0}".format(cosine(" ".join(sentence1), " ".join(sentence2)))
    print "COSINE OF CLASSIFIED SENTENCES: {0}".format(cosine(" ".join(classified_sentence1), " ".join(classified_sentence2)))
    
    
    print "--------------------------------------------------------------------"
    print "--------------------------------------------------------------------"

    print "WITHOUT CLUSTERING"
    
    hmm = HMM(4, num_articles, use_clusters=False)
    
    sentence1 = tuple(articles[0][sentence_num].split())
    print "CLASSIFYING :\n{0}".format(sentence1)
    
    classified_sentence1 = set()
    groups = hmm.classify_sentence(sentence1)
    for group in groups:
        cluster = hmm.clusters[group]
        for phrase in cluster:
            for word in phrase:
                classified_sentence1.add(word)
        print "ID: {0}\t{1}".format(group, cluster)
        
    print "----------------------------------------------------------"   
    
    sentence2 = tuple(articles[1][sentence_num].split())
    print "CLASSIFYING :\n{0}".format(sentence2)
    
    classified_sentence2 = set()
    groups = hmm.classify_sentence(sentence2)
    for group in groups:
        cluster = hmm.clusters[group]
        for phrase in cluster:
            for word in phrase:
                classified_sentence2.add(word)
        print "ID: {0}\t{1}".format(group, cluster)
        
    print "----------------------------------------------------------"  
    
    print "COSINE OF SENTENCES: {0}".format(cosine(" ".join(sentence1), " ".join(sentence2)))
    print "COSINE OF CLASSIFIED SENTENCES: {0}".format(cosine(" ".join(classified_sentence1), " ".join(classified_sentence2)))
    