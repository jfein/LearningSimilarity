from util import SourceArticles, time_function
#from hmm import HMM
import heapq


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

def sim_group_average(spin_groups, cluster1, cluster2):
    total = 0.0

    for sg1 in cluster1:
        for sg2 in cluster2:
            total+= spin_group_sim(spin_groups[sg1], spin_groups[sg2])

    return total / (len(cluster1) * len(cluster2))

def sim_complete_link(spin_groups, cluster1, cluster2):
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
            sim = min(sim, spin_group_sim(spin_groups[sg1], spin_groups[sg2]))

    return sim

def sim_single_link(cluster1, cluster2):
    '''
    single link similarity

    '''
    sim = 0.0
    for sg1 in cluster1:
        for sg2 in cluster2:
            sim = max(sim, spin_group_sim(sg1, sg2))

    return sim


@time_function
def improved_hac(spin_groups,
    spin_groups_inverse,
    inverted_phrase_index,
    stopping_threshold=.5,
    stopping_num_of_groups=None,
    sim_func=sim_complete_link,
    print_out=False):

    if print_out:
        num_one_word_spin_groups = 0
        for sg in spin_groups:
            if len(sg) == 1:
                num_one_word_spin_groups+= 1

    new_spin_groups_inverse = dict(spin_groups_inverse)
    # Originally this is spin_groups
    clusters = dict((id, [id]) for id in xrange(len(spin_groups)))
    clusters_inverse = dict((id, id) for id in xrange(len(spin_groups)))

    # N heaps. sim_heaps[cid] is a heap keeping track of the
    # similarities between cid and every other cluster
    sim_heaps = {}

    # Map of cid -> all entries in all the heaps of the form [sim, cid', Valid]
    # where cid == cid'. We keep this so when we merge clusters we can easily invalidate
    # all the entries pointing to the prior clusters without having to search every element
    # of all N heaps. This brings that step down from O(n^2) to O(n) at the cost
    # of being extremely fucking confusing
    entries_map = dict((cid, []) for cid in clusters)

    '''
    Fill the heaps with the initial similarities of all clusters
    This step should be n^2 log(n) since there are n^2 pairs
    and each pair requires an insert into a heap of n^2 items
    (So actually n^2 log(n^2) but thats n^2 log(n))
    '''
    for cid1, cluster1 in clusters.iteritems():
        sim_heap = []
        sgid, = cluster1
        cids = set([cid1])
        for phrase in spin_groups[sgid]:
            for cid2 in inverted_phrase_index[phrase]:
                if cid2 not in cids:
                    cids.add(cid2)
                    sim = sim_func(spin_groups, cluster1, clusters[cid2])
                    entry = [-sim, cid2, True]
                    heapq.heappush(sim_heap, entry)
                    entries_map[cid2].append(entry)
        sim_heaps[cid1] = sim_heap



    while True:
        assert(len(clusters) == len(sim_heaps))
        assert(len(clusters) == len(entries_map))

        # Need to find the max similarity
        max_sim = None
        max_cids = None

        '''
        This part is expected O(N), worse case O(n^2).
        Go through each N heaps and get the first valid
        entry which is expected O(1), worse case O(N)
        '''
        for cid1, sim_heap in sim_heaps.iteritems():

            # Remove all the invalid items from the top
            while len(sim_heap) > 0 and not sim_heap[0][-1]:
                heapq.heappop(sim_heap)

            if len(sim_heap) == 0:
                continue
                #print "ERROR : sim heap {0} has length 0".format(cid1)

            if -sim_heap[0][0] > max_sim:
                max_sim = -sim_heap[0][0]
                max_cids = (cid1, sim_heap[0][1])

        if not max_sim:
            break

        if not stopping_num_of_groups and max_sim < stopping_threshold:
            break

        ''' Now we know we need to merge cid1, cid2 '''
        ''' We arbitrarily choose to merge cluster2 into cluster1'''

        cid1, cid2 = max_cids

        # print "Merging clusters {cid1} and {cid2} with similarity {max_sim}".format(**locals())

        # First update our clusters map
        clusters[cid1] = clusters[cid1] + clusters[cid2]


        # Now update the clusters_inverse
        for sgid in clusters[cid2]:
            clusters_inverse[sgid] = cid1

        # Now invalidate the similarities
        for entry in entries_map[cid1]:
            entry[-1] = False

        for entry in entries_map[cid2]:
            entry[-1] = False

        del clusters[cid2]
        del sim_heaps[cid2]
        del entries_map[cid2]

        # Go through and add entries only to
        # clusters[cid1] is a list of spin group ids

        already_simmed_cids = set([cid1])

        for sgid in clusters[cid1]:
            for phrase in spin_groups[sgid]:
                for sgid in inverted_phrase_index[phrase]:
                    cid = clusters_inverse[sgid]
                    if cid in already_simmed_cids:
                        continue
                    already_simmed_cids.add(cid)
                    sim = sim_func(spin_groups, clusters[cid], clusters[cid1])

                    entry1 = [-sim, cid, True]
                    entries_map[cid].append(entry1)
                    heapq.heappush(sim_heaps[cid1], entry1)
        '''
        for cid, cluster in clusters.iteritems():
            if cid == cid1:
                continue

            sim = sim_func(spin_groups, cluster, clusters[cid1])
            # Create two entries. One for sim_heaps[cid]
            # One for sim_heaps[cid1]

            entry1 = [-sim, cid, True]
            entries_map[cid].append(entry1)
            heapq.heappush(sim_heaps[cid1], entry1)
        '''
        if stopping_num_of_groups and len(clusters) <= stopping_num_of_groups:
            break

    # Now we want to build the new spin groups
    # cid -> sgid

    new_spin_groups = {}
    for cid in clusters:
        new_spin_group = set()
        for sgid in clusters[cid]:
            for phrase in spin_groups[sgid]:
                new_spin_group.add(phrase)
        new_spin_groups[cid] = frozenset(new_spin_group)

    if print_out:
        num_one_word_clustered_spin_groups = 0
        for cluster in clusters.values():
            if len(cluster) == 1 and len(spin_groups[cluster[0]]) == 1:
                  num_one_word_clustered_spin_groups+= 1


        print "One phrase spin groups before : ", num_one_word_spin_groups
        print "One phrase spin groups after : ", num_one_word_clustered_spin_groups

        print "Clustered {0} spin groups into {1} clusters".format(len(spin_groups), len(clusters))

        for cid, cluster in clusters.iteritems():
            print 'Cluster {0}'.format(cid)
            for sgid in cluster:
                sg = spin_groups[sgid]
                print '\t', "|".join(" ".join(sg_tuple) for sg_tuple in sg)

    return clusters_inverse, new_spin_groups



@time_function
def hac(spin_groups,
        spin_groups_inverse,
        stopping_threshold=.75,
        stopping_num_of_groups=None,
        sim_func=sim_complete_link,
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
    clusters = dict((cluster_id, [spin_group]) for (cluster_id, spin_group) in enumerate(spin_groups))

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
        '''
        for cid, cluster in clusters.iteritems():
            print 'Cluster {0}'.format(cid)
            for sg in cluster:
                print '\t', "|".join(" ".join(sg_tuple) for sg_tuple in sg)
        '''
    return new_spin_groups_inverse



if __name__ == "__main__":
    print_out=True
    compare_clusters=False

    '''
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
    spin_groups_inverse = dict((sg, id) for (id, sg) in enumerate(spin_groups))

    '''
    hmm = HMM(ngram = 2, num_articles=75)
    spin_groups = hmm.spin_groups
    spin_groups_inverse = hmm.spin_groups_inverse
    phrase_index = hmm.phrases

    print "Done building HMM...now about to cluster"

    '''
    improved_hac_inverse = improved_hac(spin_groups,
                               spin_groups_inverse,
                               sim_func=sim_complete_link,
                               stopping_threshold=1.0/2.0,
                               print_out=False)
    '''

    sgid_to_cid, new_spin_groups = improved_hac(spin_groups,
                               spin_groups_inverse,
                               sim_func=sim_group_average,
                               inverted_phrase_index=phrase_index,
                               stopping_threshold=1.0/2.0,
                               print_out=True)

    for new_sgid, new_spin_group in new_spin_groups.iteritems():
        print "New spin group id {0}".format(new_sgid)
        print "\t{0}".format("|".join(" ".join(phrase) for phrase in new_spin_group))


