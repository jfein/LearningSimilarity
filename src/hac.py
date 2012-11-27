from util import SourceArticles

def make_spin_group(phrases):
    sg = set()
    for phrase in phrases:
        words = tuple(phrase.split())
        sg.add(words)
    return frozenset(sg)

def spin_group_sim(sg1, sg2):
    '''
    Similarity of two spin groups, which
    is the number of elements in common divided
    by number of unique elements
    |{sg1 intersect sg2}| / |{sg1 union sg2}|
    '''
    return float(len(sg1.intersection(sg2))) / len(sg1.union(sg2))

def sim_func(cluster1, cluster2):
    '''
    Returns the similarity of two clusters
    Clusters are lists of spin groups
    A spin group is a frozen set of phrases
    Each phrase is a tuple of words
    
    Returns a float between 0.0 and 1.0
    
    Could be 
    [set('Like', 'Love', 'Adore'), set('Like, Love')]
    [set('dog, canine']]
    
    Should return complete-line: i.e. the minimum similarity
    between any two elements
    
    '''
    sim = 1.0
    for sg1 in cluster1:
        for sg2 in cluster2:
            sim = min(sim, spin_group_sim(sg1, sg2))

    return sim


def hac(spin_groups,
        spin_groups_inverse,
        stopping_threshold=.75,
        stopping_num_of_groups=None,
        print_out=False):
    """
    Takes in a list of spin groups where each index corresponds
    to the sgid and a mapping of that sgid back to the spin group.
    
    Returns a new mapping of spin group to id. Each spin group should
    be mapped to it's new cluster id (which may or may not be the same as
    it's old sgid)
    
    So 
    ['really like|like|adore', 'like|adore', 'dog|canine'],
    {'really like|like|adore' : 0, 'like|adore' : 1, 'dog|canine':2}
    
    Would return something like
    {'really like|like|adore' : 0, 'like|adore' : 0, 'dog|canine':2}
    
    If stopping_num_of_groups is provided we cluster until we have that
    number of spin groups remaining. Otherwise we cluster until there
    are no two clusters with similarity greater than stopping_threshold remaining
    """
    new_spin_groups_inverse = dict(spin_groups_inverse)

    def update_sgids(cluster, new_cid):
        for element in cluster:
            if isinstance(element, list):
                update_sgids(element, new_cid)
            else:
                new_spin_groups_inverse[element] = new_cid

    # Clusters is a map of cluster id -> clusters

    # Originally this is spin_groups
    clusters = {cluster_id : [spin_group] for (cluster_id, spin_group) in enumerate(spin_groups)}

    while True:
        best_sim, best_clusters = None, None
        for cid1 in clusters:
            for cid2 in clusters:
                if cid1 == cid2:
                    continue

                sim = sim_func(clusters[cid1], clusters[cid2])

                if sim > best_sim:
                    best_sim = sim
                    best_clusters = (cid1, cid2)

        if not stopping_num_of_groups and best_sim < stopping_threshold:
            break

        # Need to pick new cid. Just use cid1
        best_cid1, best_cid2 = best_clusters
        clusters[best_cid1] = clusters[best_cid1] + clusters[best_cid2]

        update_sgids(clusters[best_cid1], best_cid1)
        update_sgids(clusters[best_cid2], best_cid1)

        del clusters[best_cid2]

        if stopping_num_of_groups and len(clusters) <= stopping_num_of_groups:
            break

    if print_out:
        print "Clustered {0} spin groups into {1} clusters".format(len(spin_groups), len(clusters))

        for cid, cluster in clusters.iteritems():
            print 'Cluster {0}'.format(cid)
            for sg in cluster:
                print '\t', "|".join(" ".join(sg_tuple) for sg_tuple in sg)

    return new_spin_groups_inverse

if __name__ == "__main__":
    crude_spin_groups = []
    crude_spin_groups.append(['like', 'love', 'adore'])
    crude_spin_groups.append(['like', 'love'])
    crude_spin_groups.append(['like', 'love', 'really like'])
    crude_spin_groups.append(['like', 'love', 'adore', 'really adore'])

    crude_spin_groups.append(['dog', 'canine'])
    crude_spin_groups.append(['cat', 'feline'])

    crude_spin_groups.append(['good', 'bad'])
    crude_spin_groups.append(['good', 'bad', 'very good', 'very bad'])
    crude_spin_groups.append(['good', 'bad', 'really good', 'really bad'])

    spin_groups = [make_spin_group(sg) for sg in crude_spin_groups]
    spin_groups_inverse = {sg : id for (id, sg) in enumerate(spin_groups)}

    new_inverse = hac(spin_groups, spin_groups_inverse, stopping_threshold=2.0 / 3.0)

    for sg, sgid in new_inverse.iteritems():
        print "|".join(" ".join(sg_tuple) for sg_tuple in sg), " : ", sgid


