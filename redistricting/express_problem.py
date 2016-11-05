"""
Riddler express problem from
http://fivethirtyeight.com/features/rig-the-election-with-math/
"""
import numpy as np
import cPickle as pickle
from find_winning_districting import District
from find_winning_districting import search_configurations


if __name__ == "__main__":
    voter_distribution = np.array([[1, 1, 0, 0, 0],
                                   [0, 1, 1, 0, 1],
                                   [1, 0, 0, 0, 0],
                                   [0, 0, 1, 1, 0],
                                   [0, 0, 0, 0, 1]]
                                  )
    init_districts = [District([(i, j) for j in range(5)])
                      for i in range(5)]

    max_wins, final_configuration \
        = search_configurations(voter_distribution,
                                init_districts,
                                num_district_wins_stop = 3)

    print "Max districts won in any configuration:", max_wins
    pickle.dump(final_configuration, open('final_config.pkl', 'w'))
