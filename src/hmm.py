from util import SourceArticles, cosine, PORTER_STEMMER

class HMM():

    def __init__(self, ngram):
        self.ngram = ngram

        # Set up the source articles
        self.src_articles = SourceArticles(
            stdizer=PORTER_STEMMER,
            omit_stopwords=True,
            stdize_kws=True,
            stdize_article=True,
            max_phrase_size=ngram
        )
        
        self.spin_groups = [frozenset()]  # List of spin groups (spin group is a set of phrase tuples), indexed by spin group ID
        self.transitions = {}  # Mapping rom spin group ID to dict of spgid to counts
        
        spin_groups_inverse = {frozenset():0}  # Mapping from spin group to spin group ID
        
        for article_num in range(500):
            sentences = self.src_articles.get_article_sentences(article_num)

            for sentence in sentences:                    
                prev_spgid = None
            
                for spin_group in sentence:
                    # Get ID for this spin group
                    if spin_group not in spin_groups_inverse:
                        self.spin_groups.append(spin_group)
                        sgid = len(self.spin_groups) - 1
                        spin_groups_inverse[spin_group] = sgid
                    sgid = spin_groups_inverse[spin_group]
                    
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
        if src_sgid == 0 or dest_sgid == 0:
            return 1.0 / len(self.spin_groups)
        
        edges_from_src = self.transitions.get(src_sgid, {})
        if dest_sgid not in edges_from_src:
            return 0.0
        return float(edges_from_src[dest_sgid]) / sum(edges_from_src.values())
        
    def emission_prob(self, sgid, phrase):
        '''
        Returns probability that sgid will emit phrase. Phrase is a list of strings.
        '''
        if sgid == 0:
            return 1.0
            
        spin_group = self.spin_groups[sgid]
        if phrase in spin_group:
            return 1.0 / len(spin_group)
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
            for sgid in range(len(self.spin_groups)):
                for wb in range(self.ngram):
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
                        prev_delta = deltas[t-1-wb]
                        best_prev_key = None
                        max = 0.0
                        emit_prob = self.emission_prob(sgid, phrase)
                        if (emit_prob > 0.0):
                            for (prev_sgid, prev_wb), (prev_prob, prev_key) in prev_delta.iteritems():
                                value = prev_prob * self.transition_prob(prev_sgid, sgid) * emit_prob
                                if value > max:
                                    max = value
                                    best_prev_key = (prev_sgid, prev_wb)
                        if best_prev_key:
                            delta[key] = (max , best_prev_key)
                            
            deltas.append(delta)
                    
        # Find the max in the last delta
        last_delta = deltas[t]
        max_prob = 0.0
        best_kv = None
        for (sgid, wb) , (prob, (prev_sgid, prev_wb)) in last_delta.iteritems():
            if prob >= max_prob:
                max_prob = prob
                best_kv = (sgid, wb) , (prob, (prev_sgid, prev_wb))
   
        # Backtrack 
        spin_groups = []
        t = len(sentence)-1
        while t >= 0:
            (sgid, wb) , (prob, (prev_sgid, prev_wb)) = best_kv
            spin_groups.append(sgid)
            t = t - wb - 1
            best_kv = (prev_sgid, prev_wb) , deltas[t].get((prev_sgid, prev_wb), (0.0, (None, 0)))
                 
        # Returns the spin groups found
        spin_groups.reverse()
        return spin_groups
        
            

        
if __name__ == "__main__":
    hmm = HMM(4)
    
    for sgid, spin_group in enumerate(hmm.spin_groups):
        print "{0} : {1}".format(sgid, spin_group)
        
    print "--------------------------------------------------------------------"
    print "--------------------------------------------------------------------"

    
    sentence = tuple(hmm.src_articles.spin_article(200)[0].split())
    
    print len(sentence)
    print "CLASSIFYING :\n{0}".format(sentence)
    
    groups = hmm.classify_sentence(sentence)
    
    for group in groups:
        print hmm.spin_groups[group]
        
    print "--------------------------------------------------------------------" 
 
    sentence = tuple(hmm.src_articles.spin_article(200)[0].split())
    
    print len(sentence)
    print "CLASSIFYING :\n{0}".format(sentence)
    
    groups = hmm.classify_sentence(sentence)
    
    for group in groups:
        print hmm.spin_groups[group]
        