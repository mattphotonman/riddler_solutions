"""
For a given board, find a redistricting in which
a given party wins, using Monte Carlo.

http://fivethirtyeight.com/features/rig-the-election-with-math/
"""
import random
import numpy as np
import copy
from itertools import combinations

class District:
    """
    Class representing a single voting district.
    (A district is a set of a given number of
    contiguous tiles. The class allows you to
    create a non-contiguous District for use with
    the is_contiguous and get_contiguous_subdistricts
    methods, but such a District does not have well
    defined behavior under the other methods.)
    """
    def __init__(self, tiles):
        self._tiles = set(tiles)

    def __contains__(self, tile):
        return tile in self._tiles

    def __len__(self):
        return len(self._tiles)

    def return_tiles(self):
        return set(self._tiles)

    def is_contiguous(self):
        if len(self) <= 1:
            return True

        collected = set()
        queue = {list(self._tiles)[0]}
        remaining = self._tiles - queue
        while len(queue) > 0:
            new_tiles = set()
            for tile in queue:
                for new_tile in self._get_neighbors(tile, remaining):
                    new_tiles.add(new_tile)
            collected.update(queue)
            remaining.difference_update(new_tiles)
            queue = new_tiles

        return len(remaining) == 0

    def get_contiguous_subdistricts(self):
        """
        Returns a list of District objects that
        are contiguous, the union of which is
        equal to self.  If self is already
        contiguous, it will be returned as the
        sole item in the list.
        """
        if len(self) == 0:
            return []
        if len(self) == 1:
            return [District(self._tiles)]
        
        subdistricts = []
        collected = set()
        queue = {list(self._tiles)[0]}
        remaining = self._tiles - queue
        while True:
            while len(queue) > 0:
                new_tiles = set()
                for tile in queue:
                    for new_tile in self._get_neighbors(tile, remaining):
                        new_tiles.add(new_tile)
                collected.update(queue)
                remaining.difference_update(new_tiles)
                queue = new_tiles

            subdistricts.append(District(collected))

            if len(remaining) == 0: break
            
            collected = set()
            queue = {list(remaining)[0]}
            remaining.difference_update(queue)

        return subdistricts

    def find_border(self, other_district):
        """
        Return the tiles from self that
        are adjacent to any tile in other_district.
        """
        return {tile for tile in self._tiles
                if self._has_neighbors(tile, other_district)}
    
    def find_border_pairs(self, other_district):
        """
        Return the pairs of tiles from self
        and other_district that are adjacent.
        """
        border = set()
        for tile in self._tiles:
            for neighbor_tile in self._get_neighbors(tile, other_district):
                border.add((tile, neighbor_tile))
        return border

    def find_allowed_trades(self, other_district):
        """
        Return the possible trades of tiles that
        can be made between the two districts
        such that they would each remain
        contiguous.
        """
        trades = []
        for trade_tile_other in other_district.find_border(self):
            new_district_this = District(self._tiles | {trade_tile_other})
            new_district_other = District(other_district._tiles - {trade_tile_other})
            other_subdistricts = new_district_other.get_contiguous_subdistricts()
            sub_borders = [new_district_this.find_border(subdistrict)
                           for subdistrict in other_subdistricts]
            possible_trade_tiles_this = reduce(lambda x, y : x & y,
                                               sub_borders) - {trade_tile_other}
            for trade_tile_this in possible_trade_tiles_this:
                new_new_district_this = District(new_district_this._tiles - \
                                                 {trade_tile_this})
                if new_new_district_this.is_contiguous():
                    trades.append((trade_tile_this, trade_tile_other))
        return trades

    def _has_neighbors(self, tile, tile_set):
        """
        Returns True if tile has any neighbors
        in tile_set.
        """
        i, j = tile
        for delta in [-1, 1]:
            if (i + delta, j) in tile_set:
                return True
            if (i, j + delta) in tile_set:
                return True
        return False

    def _get_neighbors(self, tile, tile_set):
        neighbors = []
        i, j = tile
        for delta in [-1, 1]:
            if (i + delta, j) in tile_set:
                neighbors.append((i + delta, j))
            if (i, j + delta) in tile_set:
                neighbors.append((i, j + delta))
        return neighbors

class BaseConfiguration:
    """
    Base class for a set of districts and
    a voter distribution. Actual configuration
    classes should inherit from this and
    implement the _get_trade_probability
    method.
    """
    def __init__(self, districts, voter_distribution):
        self._voter_distribution = voter_distribution
        self._districts = districts

        self._validate_districts()
        self._compute_possible_trades()

    def __len__(self):
        return len(self._districts)

    def iterate(self):
        """
        Randomly picks one of the possible trades
        and performs that trade with probability
        given by the _get_trade_probability
        method.
        """
        trade = random.choice(self._possible_trades)
        (idx1, idx2), (tile1, tile2) = trade
        prob = self._get_trade_probability(idx1, tile1,
                                           idx2, tile2)
        if random.random() <= prob:
            self._make_trade(idx1, tile1, idx2, tile2)

    def num_districts_one_win_or_tie(self):
        return sum(self._num_one_votes(district.return_tiles()) >= \
                   int(np.ceil(len(district) / 2.))
                   for district in self._districts)

    def _validate_districts(self):
        for district in self._districts:
            assert district.is_contiguous()
        
        for district1, district2 in combinations(self._districts, 2):
            assert len(district1.return_tiles() & district2.return_tiles()) == 0

        all_tiles = reduce(lambda x, y : x | y,
                           [district.return_tiles()
                            for district in self._districts]
                           )
        assert all_tiles == {(i, j)
                             for i in range(self._voter_distribution.shape[0])
                             for j in range(self._voter_distribution.shape[1])}

    def _compute_possible_trades(self):
        self._possible_trades = []
        for (idx1, district1), (idx2, district2) \
            in combinations(enumerate(self._districts), 2):
            for trade in district1.find_allowed_trades(district2):
                self._possible_trades.append(((idx1, idx2),
                                              trade)
                                             )

    def _make_trade(self, idx_dist1, tile_dist1, idx_dist2, tile_dist2):
        new_dist1 = District((self._districts[idx_dist1].return_tiles() - \
                              {tile_dist1}) | {tile_dist2})
        new_dist2 = District((self._districts[idx_dist2].return_tiles() - \
                              {tile_dist2}) | {tile_dist1})
        self._districts[idx_dist1] = new_dist1
        self._districts[idx_dist2] = new_dist2

        self._update_possible_trades([idx_dist1, idx_dist2])

    def _update_possible_trades(self, idx_dist_list):
        """
        Update the possible trades given that only the
        districts with index in idx_dist_list have been
        updated.  (The index is with respect to the
        list self._districts.)
        """
        idx_updated = set(idx_dist_list)
        self._possible_trades = [((idx1, idx2), trade)
                                 for (idx1, idx2), trade
                                 in self._possible_trades
                                 if idx1 not in idx_updated and \
                                 idx2 not in idx_updated]
        for (idx1, district1), (idx2, district2) \
            in combinations(enumerate(self._districts), 2):
            if idx1 not in idx_updated and idx2 not in idx_updated: continue
            for trade in district1.find_allowed_trades(district2):
                self._possible_trades.append(((idx1, idx2),
                                              trade)
                                             )

    def _num_one_votes(self, tiles):
        return sum(self._voter_distribution[tile]
                   for tile in tiles)

class ClassicConfiguration(BaseConfiguration):
    """
    Computes trade probabilities in a way inspired by
    classic MCMC.
    """
    def __init__(self, districts, voter_distribution,
                 lower_prob = 0.1):
        BaseConfiguration.__init__(self, districts,
                                  voter_distribution)
        self._lower_prob = lower_prob
    
    def _get_trade_probability(self, idx1, tile1,
                               idx2, tile2):
        """
        Probability of the trade is 1.0 if it doesn't
        change or increases the number of districts
        where 1 wins.  If the number of districts
        where 1 wins decreases then the probability
        of the trade is self._lower_prob.
        """
        dist1_tiles = self._districts[idx1].return_tiles()
        dist2_tiles = self._districts[idx2].return_tiles()

        new_dist1_tiles = (dist1_tiles - {tile1}) | {tile2}
        new_dist2_tiles = (dist2_tiles - {tile2}) | {tile1}

        wins_before = int(self._num_one_votes(dist1_tiles) >= \
                       int(np.ceil(len(dist1_tiles) / 2.))) + \
            int(self._num_one_votes(dist2_tiles) >= \
             int(np.ceil(len(dist2_tiles) / 2.)))
        wins_after = int(self._num_one_votes(new_dist1_tiles) >= \
                      int(np.ceil(len(new_dist1_tiles) / 2.))) + \
            int(self._num_one_votes(new_dist2_tiles) >= \
             int(np.ceil(len(new_dist2_tiles) / 2.)))

        if wins_after < wins_before:
            return self._lower_prob
        else:
            return 1.

def search_configurations(voter_distribution, init_districts,
                          ConfigurationClass = ClassicConfiguration,
                          configuration_kwargs = {},
                          max_iter = 10000,
                          num_district_wins_stop = None,
                          vrb = True):
    configuration = ConfigurationClass(init_districts,
                                       voter_distribution,
                                       **configuration_kwargs)
    max_wins = configuration.num_districts_one_win_or_tie()
    max_win_config = copy.deepcopy(configuration)
    for iter_num in xrange(1, max_iter + 1):
        if num_district_wins_stop is not None and \
           max_wins >= num_district_wins_stop: break
        configuration.iterate()

        wins = configuration.num_districts_one_win_or_tie()
        if wins > max_wins:
            max_wins = wins
            max_win_config = copy.deepcopy(configuration)

        if vrb:
            message_at = int(max_iter / 100)
            if iter_num % message_at == 0:
                print iter_num, "iterations completed.",
                print "Districts won by 1 in current configuration:",
                print configuration.num_districts_one_win_or_tie(),
                print "Max districts won by 1:", max_wins

    return max_wins, max_win_config
