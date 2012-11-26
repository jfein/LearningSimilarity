from util import SourceArticles, cosine

class HMM():

    def __init__(self):
        src_articles = SourceArticles()
        
        sg_cnt = 0
        self.spin_groups = {}  # Mapping from set of phrases to ID
        self.transitions = {}   # Mapping rom spin group ID to dict of spgid to counts
        self.emission = {}     # 
        
        for article_num in range(1):
            txt = "I {like|love} {dogs|canines}. I {like|crave} {delicious|tasty} {snacks|dessert|candy}. He {really likes| adores} you. The {dogs|canines} {crave|really crave|need|want} {lots of|a lot of|much} attention. I {like|love} you."

            sentences = src_articles.get_article_sentences(0, txt)

            for sentence in sentences:                    
                prev_spgid = None
            
                for spin_group in sentence:
                    # Get ID for this spin group
                    if spin_group not in self.spin_groups:
                        self.spin_groups[spin_group] = sg_cnt
                        sg_cnt += 1
                    sgid = self.spin_groups[spin_group]
                    
                    # Add the edge from prev_spgid to spgid
                    transition_from_prev = self.transitions.get(prev_spgid, {})
                    transition_from_prev_to_cur = transition_from_prev.get(sgid, 0)
                    transition_from_prev_to_cur += 1
                    transition_from_prev[sgid] = transition_from_prev_to_cur
                    self.transitions[prev_spgid] = transition_from_prev
                    
                    prev_spgid = sgid
                    
    def transition_prob(self, src_sgid, dest_sgid):
        edges_from_src = self.transitions.get(src_sgid, {})
        if dest_sgid not in edges_from_src:
            return 0.0
        return float(edges_from_src[dest_sgid]) / sum(edges_from_src.values())
            
        
        
        
        
if __name__ == "__main__":
    hmm = HMM()
    
    for spin_group, sgid in hmm.spin_groups.iteritems():
        print "{0} : {1}".format(sgid, spin_group)
        
    print "--------------------------------------------------------------------"
    print "--------------------------------------------------------------------"
    
    for sgid, edge_counts in hmm.transitions.iteritems():
        print "--------------------------------"
        print "TRANSITIONS FROM {0}:\n".format(sgid)
        for k, v in edge_counts.iteritems():
            print "\t{0} : {1}".format(k, hmm.transition_prob(sgid, k))
        