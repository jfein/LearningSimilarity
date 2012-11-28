import math
from util import SourceArticles, cosine, time_function


def log(x):
    if x <= 0:
        return float("-INF")
    return math.log(x)
    

class HMM():

    def __init__(self, ngram, num_articles=None):
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
        self.transitions = {}  # Mapping rom spin group ID to dict of spgid to counts
        
        self.spin_groups_inverse = {frozenset():0}  # Mapping from spin group to spin group ID
        
        # TODO: count of unknown state???
        self.spin_group_counts = {0:0} # Mapping from spin group ID to number of occurances of that spin group
        
        self.phrases = {} # Set of all unique phrases
        
        for article_num in range(num_articles):
            sentences = self.src_articles.get_article_sentences(article_num)

            for sentence in sentences:                    
                prev_spgid = None
            
                for spin_group in sentence:
                    # Get ID for this spin group
                    if spin_group not in self.spin_groups_inverse:
                        self.spin_groups.append(spin_group)
                        sgid = len(self.spin_groups) - 1
                        self.spin_groups_inverse[spin_group] = sgid
                        # Map phrases in this spin group to this spin group ID
                        for phrase in spin_group:
                            if phrase not in self.phrases:
                                self.phrases[phrase] = []
                            self.phrases[phrase].append(sgid)                      
                    sgid = self.spin_groups_inverse[spin_group]
                    self.spin_group_counts[sgid] = self.spin_group_counts.get(sgid, 0) + 1
                    
                    # Add the edge from prev_spgid to spgid
                    transition_from_prev = self.transitions.get(prev_spgid, {})
                    transition_from_prev_to_cur = transition_from_prev.get(sgid, 0)
                    transition_from_prev_to_cur += 1
                    transition_from_prev[sgid] = transition_from_prev_to_cur
                    self.transitions[prev_spgid] = transition_from_prev
                    
                    prev_spgid = sgid
                    
        self.CHe = sum(self.spin_group_counts.values())
        self.Ne = len(self.spin_group_counts)
                    
    def transition_prob(self, src_sgid, dest_sgid):
        '''
        Returns probability that src_sgid will transition to dest_sgid.
        Uses Witten-Bell smoothing:
            http://www.ee.columbia.edu/~stanchen/e6884/labs/lab3/x207.html
        '''
        edges_from_src = self.transitions.get(src_sgid, {})
        # "unknown" state transitions to all others
        if src_sgid == 0:
            edges_from_src = self.spin_group_counts
        
        # number of times dest_sgid occurs
        Cd = float(self.spin_group_counts.get(dest_sgid, 0))
        
        # count of transitions from src_sgid to dest_sgid
        Csd = float(edges_from_src.get(dest_sgid, 0))
        
        # number of total transitions from src_sgid
        CHs = float(sum(edges_from_src.values()))
        # numver of unique transitions from src_sgid
        Ns = float(len(edges_from_src))
        
        # No transitions from src_sgid, return 0
        if CHs == 0.0:
            return 0.0
        
        Pmle = Csd / CHs
        Pb = (Cd + 1) / (self.CHe + self.Ne)
        
        return ((CHs / (CHs + Ns)) * Pmle) + ((Ns / (CHs + Ns)) * Pb)
        #return Pmle
        #return (count + 1.0) / (float(len(self.spin_groups)) + float(sum(edges_from_src.values())))
        
    def emission_prob(self, sgid, phrase):
        '''
        Returns probability that sgid will emit phrase. Phrase is a list of strings.
        '''
        if sgid == 0:
            if len(phrase) == 1 and phrase not in self.phrases:
                return 1.0
            return 0.0
            
        spin_group = self.spin_groups[sgid]
        if phrase in spin_group:
            return 1.0 / len(spin_group)
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
            for sgid in range(len(self.spin_groups)):
                for wb in range(self.ngram):
                    key = (sgid, wb)
                    
                    # Make sure theres enough words back
                    if t-wb < 0:
                        delta[key] = (float("-INF"), (None, 0))
                        continue
                    
                    # Extract the phrase
                    phrase = sentence[t-wb:t+1]
                                        
                    # Is a start probability
                    if t-1-wb < 0:
                        value = log(self.transition_prob(None, sgid)) + log(self.emission_prob(sgid, phrase))
                        delta[key] = (value , (None, 0))
                    # Not a start probability
                    else:
                        prev_delta = deltas[t-1-wb]
                        best_prev_key = None
                        max = None
                        emit_prob = self.emission_prob(sgid, phrase)
                        if (emit_prob > 0.0):
                            for (prev_sgid, prev_wb), (prev_prob, prev_key) in prev_delta.iteritems():
                                value = prev_prob + log(self.transition_prob(prev_sgid, sgid)) + log(emit_prob)
                                if value > max:
                                    max = value
                                    best_prev_key = (prev_sgid, prev_wb)
                        if best_prev_key:
                            delta[key] = (max , best_prev_key)
                            
            deltas.append(delta)
                    
        # Find the max in the last delta
        last_delta = deltas[t]
        max_prob = None
        best_kv = None
        for (sgid, wb) , (prob, prev_key) in last_delta.iteritems():
            if prob >= max_prob:
                max_prob = prob
                best_kv = (sgid, wb) , (prob, prev_key)
   
        # Backtrack 
        spin_groups = []
        t = len(sentence)-1
        while t >= 0:
            (sgid, wb) , (_, prev_key) = best_kv
            spin_groups.append(sgid)
            t = t - wb - 1
            best_kv = prev_key , deltas[t].get(prev_key, (float("-INF"), (None, 0)))
                 
        # Returns the spin groups found
        spin_groups.reverse()
        return spin_groups
        
            

        
if __name__ == "__main__":
    hmm = HMM(4, 10)
    
    for sgid, spin_group in enumerate(hmm.spin_groups):
        print "{0} : {1}".format(sgid, spin_group)
        
    print "--------------------------------------------------------------------"
    print "--------------------------------------------------------------------"

    article_num = 1001
    sentence_num = 0
    
    print "ORIGINAL SENTENCE:"
    print hmm.src_articles.get_article_sentences(article_num)[sentence_num]
    print "--------------------------------------------------------------------" 
    
    #TODO: look at 202 sentence 1
    articles = hmm.src_articles.spin_dissimilar_articles(article_num, 2)
    
    sentence1 = tuple(articles[0][sentence_num].split())
    print len(sentence1)
    print "CLASSIFYING :\n{0}".format(sentence1)
    
    classified_sentence1 = set()
    groups = hmm.classify_sentence(sentence1)
    for group in groups:
        spin_group = hmm.spin_groups[group]
        for phrase in spin_group:
            for word in phrase:
                classified_sentence1.add(word)
        print "ID: {0}\t{1}".format(group, spin_group)
        
    print "--------------------------------------------------------------------"   
    
    sentence2 = tuple(articles[1][sentence_num].split())
    print len(sentence2)
    print "CLASSIFYING :\n{0}".format(sentence2)
    
    classified_sentence2 = set()
    groups = hmm.classify_sentence(sentence2)
    for group in groups:
        spin_group = hmm.spin_groups[group]
        for phrase in spin_group:
            for word in phrase:
                classified_sentence2.add(word)
        print "ID: {0}\t{1}".format(group, spin_group)
        
    print "--------------------------------------------------------------------"  
    
    print "COSINE OF SENTENCES: {0}".format(cosine(" ".join(sentence1), " ".join(sentence2)))
    print "COSINE OF CLASSIFIED SENTENCES: {0}".format(cosine(" ".join(classified_sentence1), " ".join(classified_sentence2)))
    