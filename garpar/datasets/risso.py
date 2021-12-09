# This file is part of the
#   Garpar Project (https://github.com/quatrope/garpar).
# Copyright (c) 2021, 2022, Nadia Luczywo, Juan Cabral and QuatroPe
# License: MIT
#   Full Text: https://github.com/quatrope/garpar/blob/master/LICENSE

# =============================================================================
# IMPORTS
# =============================================================================

import attr

import numpy as np

import scipy.stats

from . import base


# =============================================================================
# UTILS
# =============================================================================


def argnearest(arr, v):
    diff = np.abs(np.subtract(arr, v))
    idx = np.argmin(diff)
    return idx


# =============================================================================
# NORMAL
# =============================================================================


class RissoMixin:
    def risso_candidate_entropy(self, windows_size):
        if windows_size <= 0:
            raise ValueError("'windows_size' must be > 0")

        loss_probability = np.linspace(0.0, 1.0, num=windows_size + 1)

        # Se corrigen probabilidades porque el cálculo de la entropía trabaja
        # con logaritmo y el logaritmo de cero no puede calcularse
        epsilon = np.finfo(loss_probability.dtype).eps
        loss_probability[0] = epsilon
        loss_probability[-1] = 1 - epsilon

        # Calcula entropy
        first_part = loss_probability * np.log2(loss_probability)
        second_part = (1 - loss_probability) * np.log2(1 - loss_probability)

        modificated_entropy = -1 * (first_part + second_part)
        return modificated_entropy, loss_probability

    def get_window_loss_probability(self, windows_size, entropy):
        h_candidates, loss_probabilities = self.risso_candidate_entropy(
            windows_size
        )
        idx = argnearest(h_candidates, entropy)
        loss_probability = loss_probabilities[idx]

        return loss_probability


class RissoNormal(RissoMixin, base.PortfolioMakerABC):

    mu = base.hparam(default=0, converter=float)
    sigma = base.hparam(default=0.2, converter=float)

    def make_stock_price(self, price, loss, random):
        if price == 0.0:
            return 0.0
        sign = -1 if loss else 1
        day_return = sign * np.abs(random.normal(self.mu, self.sigma))
        new_price = price + day_return
        return 0.0 if new_price < 0 else new_price


class RissoLevyStable(RissoMixin, base.PortfolioMakerABC):

    alpha = base.hparam(1, converter=float)
    beta = base.hparam(0, converter=float)
    delta = base.hparam(0, converter=float)  # loc
    gamma = base.hparam(1, converter=float)  # scale

    _levy_stable = attr.ib(repr=False, init=False)

    @_levy_stable.default
    def _levy_stable_default(self):
        return scipy.stats.levy_stable(
            alpha=self.alpha, beta=self.beta, loc=self.delta, scale=self.gamma
        )

    def make_stock_price(self, price, loss, random):
        if price == 0.0:
            return 0.0
        sign = -1 if loss else 1
        day_return = sign * np.abs(self._levy_stable.rvs(random_state=random))
        new_price = price + day_return
        return 0.0 if new_price < 0 else new_price