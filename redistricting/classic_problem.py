"""
Riddler classic problem from
http://fivethirtyeight.com/features/rig-the-election-with-math/
"""
import numpy as np
import cPickle as pickle
from find_winning_districting import District
from find_winning_districting import search_configurations


if __name__ == "__main__":
    voter_distribution = np.array([[0] * 4 + [1, 0, 1, 1] + [0] * 6,
                                   [0, 0, 0, 1, 1, 0, 1, 1] + [0] * 6,
                                   [0] * 4 + [1, 0, 0, 1, 1, 1] + [0] * 4,
                                   [0] * 4 + [1] * 6 + [0] * 4,
                                   [0, 0, 0, 1, 1, 1] + [0] * 8,
                                   [0, 0, 0, 1, 1] + [0] * 9,
                                   [0, 0, 0, 1, 1, 1, 0, 0, 1, 1] + [0] * 4,
                                   [1, 1, 1, 0, 1, 1, 1, 0, 1, 1] + [0] * 4,
                                   [0, 0, 1, 0, 0, 0] + [1] * 6 + [0, 0],
                                   [0, 1, 1, 0, 0] + [1] * 7 + [0, 0]]
                                  )

    init_districts = []
    current_list = []
    for i in range(10):
        if i % 2:
            j_range = range(13, -1, -1)
        else:
            j_range = range(14)
        for j in j_range:
            current_list.append((i, j))
            if len(current_list) == 20:
                init_districts.append(District(current_list))
                current_list = []

    max_wins, best_configuration \
        = search_configurations(voter_distribution,
                                init_districts)

    print "Max districts won in any configuration:", max_wins
    pickle.dump(best_configuration, open('best_config_classic.pkl', 'w'))
