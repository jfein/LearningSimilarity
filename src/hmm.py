from util import SourceArticles, cosine, PORTER_STEMMER

class HMM():

    def __init__(self):
        # Set up the source articles
        src_articles = SourceArticles(
            stdize_kws=True,
            stdize_body=False,
            stemmer=PORTER_STEMMER,
            include_nested=True,
            omit_stopwords=False,
            max_phrase_size=5
        )
        
        self.spin_groups = []  # List of spin groups (spin group is a set of phrase tuples), indexed by spin group ID
        self.transitions = {}  # Mapping rom spin group ID to dict of spgid to counts
        self.emission = {}     # 
        
        for article_num in range(1):
            txt = "{dogs|canines} are fun. I {like|love} {dogs|canines}. I {crave|really crave|need|want} {delicious|tasty} {snacks|dessert|candy}. He {really likes| adores} you. The {dogs|canines} {crave|really crave|need|want} {lots of|a lot of|much} attention. I {like|love} you."
        
            sentences = src_articles.get_article_sentences(article_num, txt)

            for sentence in sentences:                    
                prev_spgid = None
            
                for spin_group in sentence:
                    # Get ID for this spin group
                    if spin_group not in self.spin_groups:
                        self.spin_groups.append(spin_group)
                    sgid = self.spin_groups.index(spin_group)
                    
                    # Add the edge from prev_spgid to spgid
                    transition_from_prev = self.transitions.get(prev_spgid, {})
                    transition_from_prev_to_cur = transition_from_prev.get(sgid, 0)
                    transition_from_prev_to_cur += 1
                    transition_from_prev[sgid] = transition_from_prev_to_cur
                    self.transitions[prev_spgid] = transition_from_prev
                    
                    prev_spgid = sgid
                    
    def transition_prob(self, src_sgid, dest_sgid):
        '''
        Returns probability that src_sgid will transition to dest_sgid
        '''
        edges_from_src = self.transitions.get(src_sgid, {})
        if dest_sgid not in edges_from_src:
            return 0.0
        return float(edges_from_src[dest_sgid]) / sum(edges_from_src.values())
        
    def emission_prob(self, sgid, phrase):
        '''
        Returns probability that sgid will emit phrase. Phrase is a list of strings.
        '''
        spin_group = self.spin_groups[sgid]
        if phrase in spin_group:
            return 1.0 / len(spin_group)
        else:
            return 0.0
            
    def classify_sentence(self, sentence, n=2):
        '''
        Returns the most likely sequence of spin groups that could have generated sentence
        n is the number of n-grams to consider
        '''
        deltas = []
        
        for t in range(len(sentence)):
            delta = {}
            for sgid in range(len(self.spin_groups)):
                for wb in range(n):
                    key = (sgid, wb)
                    
                    # Make sure theres enough words back
                    if t-wb < 0:
                        delta[key] = (0.0, (None, 0))
                        continue
                    
                    # Extract the phrase
                    phrase = sentence[t-wb:t+1]
                                        
                    # Is a start probability
                    if t-1-wb < 0:
                        value = self.transition_prob(None, sgid) * self.emission_prob(sgid, phrase)
                        delta[key] = (value , (None, 0))
                        
                    # Not a start probability
                    else:
                        assert(t-1-wb >= 0)
                        prev_delta = deltas[t-1-wb]
                        best_prev_key = None
                        max = 0.0
                        for (prev_sgid, prev_wb), (prob, prev_key) in prev_delta.iteritems():
                            value = prob * self.transition_prob(prev_sgid, sgid) * self.emission_prob(sgid, phrase)
                            if value >= max:
                                max = value
                                best_prev_key = (prev_sgid, prev_wb)
                        assert(best_prev_key)
                        delta[key] = (max , best_prev_key)

            deltas.append(delta)
                    
        # Find the max in the last delta
        last_delta = deltas[t]
        max_prob = 0.0
        best_key = None
        for (sgid, wb) , (prob, prev_key) in last_delta.iteritems():
            if prob >= max_prob:
                max_prob = prob
                best_key = (sgid , wb)
   
        # Backtrack 
        spin_groups = []
        t = len(sentence)-1
        while t >= 0:
            spin_groups.append(best_key[0])
            next_best_key = deltas[t][best_key][1]
            next_t = t - best_key[1] - 1
            t = next_t
            best_key = next_best_key
                 
        # Returns the spin groups found
        spin_groups.reverse()
        return spin_groups
        
            

        
if __name__ == "__main__":
    hmm = HMM()
    
    for sgid, spin_group in enumerate(hmm.spin_groups):
        print "{0} : {1}".format(sgid, spin_group)
        
    print "--------------------------------------------------------------------"
    print "--------------------------------------------------------------------"
    '''
    for sgid, edge_counts in hmm.transitions.iteritems():
        print "--------------------------------"
        print "TRANSITIONS FROM {0}:\n".format(sgid)
        for k, v in edge_counts.iteritems():
            print "\t{0} : {1}".format(k, hmm.transition_prob(sgid, k))
    '''
    
    sentence = ("dogs", "really", "crave", "tasty", "snacks")
    
    groups = hmm.classify_sentence(sentence)
    
    for group in groups:
        print hmm.spin_groups[group]
        