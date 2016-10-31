"""
Find the best (and worst) coin placements for
the deadly board game:

http://fivethirtyeight.com/features/can-you-survive-this-deadly-board-game/
"""

class LandingProbability:
    """
    Class for calculating the probability of
    landing on any coin for each placement
    of the coins.
    """
    def __init__(self, N, max_pos_first_coin = 6):
        self._N = N
        self._max_pos_first_coin = max_pos_first_coin
        self._calculate_all()

    def returnPMatrix(self, n_coins):
        if n_coins == 1:
            return {pos : p for pos, p
                    in self._P_one_coin.iteritems()
                    if pos > 0}
        elif n_coins == 2:
            return {(pos1, pos2) : p for (pos1, pos2), p
                    in self._P_two_coins.iteritems()
                    if pos1 > 0}
        elif n_coins == 3:
            return {(pos1, pos2, pos3) : p
                    for (pos1, pos2, pos3), p
                    in self._P_three_coins.iteritems()
                    if pos1 > 0}

    def _calculate_all(self):
        self._calculate_one_coin()
        self._calculate_two_coins()
        self._calculate_three_coins()

    def _calculate_one_coin(self):
        self._P_one_coin = {0 : 1.}
        for pos in range(1, self._N + 1):
            self._P_one_coin[pos] = self._calc_P_one_coin(pos)

    def _calc_P_one_coin(self, pos):
        return sum(self._get_P_one_coin(pos - i)
                   for i in range(1, 7)) / 6.

    def _get_P_one_coin(self, pos):
        if pos >= 0:
            return self._P_one_coin[pos]
        else:
            return 0.

    def _calculate_two_coins(self):
        self._P_two_coins = {(0, pos) : 1.
                             for pos in range(1, self._N + 1)}
        for pos1 in range(1, self._N):
            for pos2 in range(pos1 + 1, self._N + 1):
                self._P_two_coins[(pos1, pos2)] = self._calc_P_two_coins(pos1, pos2)

    def _calc_P_two_coins(self, pos1, pos2):
        return sum(self._get_P_two_coins(pos1 - i, pos2 - i)
                   for i in range(1, 7)) / 6.

    def _get_P_two_coins(self, pos1, pos2):
        """
        Assume pos2 > pos1
        """
        if pos1 >= 0:
            return self._P_two_coins[(pos1, pos2)]
        else:
            return self._get_P_one_coin(pos2)

    def _calculate_three_coins(self):
        self._P_three_coins = {(0, pos2, pos3) : 1.
                               for pos2 in range(1, self._N)
                               for pos3 in range(pos2 + 1, self._N + 1)}
        for pos1 in range(1, self._max_pos_first_coin + 1):
            for pos2 in range(pos1 + 1, self._N):
                for pos3 in range(pos2 + 1, self._N + 1):
                    self._P_three_coins[(pos1, pos2, pos3)] = self._calc_P_three_coins(pos1, pos2, pos3)

    def _calc_P_three_coins(self, pos1, pos2, pos3):
        return sum(self._get_P_three_coins(pos1 - i, pos2 - i, pos3 - i)
                   for i in range(1, 7)) / 6.

    def _get_P_three_coins(self, pos1, pos2, pos3):
        """
        Assume pos3 > pos2 > pos1
        """
        if pos1 >= 0:
            return self._P_three_coins[(pos1, pos2, pos3)]
        else:
            return self._get_P_two_coins(pos2, pos3)


if __name__ == "__main__":
    prob = LandingProbability(1000)
    P = prob.returnPMatrix(3)

    print "Max probability of landing on a coin:",
    print max(P.iteritems(), key = lambda (k, v) : v)
    print "Min probability of landing on a coin:",
    print min(P.iteritems(), key = lambda (k, v) : v)

    print "Max probability of landing on a coin if coins are separated by at least 2 spaces:",
    print max(( ((pos1, pos2, pos3), p)
                for ((pos1, pos2, pos3), p) in P.iteritems()
                if pos2 - pos1 > 1 and pos3 - pos2 > 1
                ),
              key = lambda (k, v) : v)
    print "Min probability of landing on a coin if coins are separated by at least 2 spaces:",
    print min(( ((pos1, pos2, pos3), p)
                for ((pos1, pos2, pos3), p) in P.iteritems()
                if pos2 - pos1 > 1 and pos3 - pos2 > 1
                ),
              key = lambda (k, v) : v)
