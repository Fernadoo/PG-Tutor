"""
Bayesian model for AI tutoring system using Poisson-Gamma conjugate priors.

This module implements the core mathematical framework for modeling student
knowledge levels using Bayesian inference with Poisson-distributed observations
and Gamma-distributed priors for the rate parameter lambda.
"""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Any


class BayesianKnowledgeModel:
    """
    Bayesian model for student knowledge level estimation.

    Uses Poisson-Gamma conjugate prior relationship:
    - Likelihood: X ~ Poisson(λ)
    - Prior: λ ~ Gamma(α, β)
    - Posterior: λ|X ~ Gamma(α + Σx_i, β + n)
    """

    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """
        Initialize the Bayesian model with Gamma prior parameters.

        Args:
            alpha: Shape parameter of Gamma prior
            beta: Rate parameter of Gamma prior
        """
        self.alpha = alpha
        self.beta = beta
        self.posterior_alpha = alpha
        self.posterior_beta = beta

        # Track history for visualization
        self.lambda_history = []
        self.observation_history = []

    def update_belief(self, observations: np.ndarray) -> Tuple[float, float]:
        """
        Update the posterior distribution with new observations.

        Args:
            observations: Array of observed student performance levels

        Returns:
            Tuple of (posterior_alpha, posterior_beta) parameters
        """
        n = len(observations)
        sum_x = np.sum(observations)

        # Gamma posterior update: Gamma(α + Σx_i, β + n)
        self.posterior_alpha = self.posterior_alpha + sum_x
        self.posterior_beta = self.posterior_beta + n

        # Store history for visualization
        self.lambda_history.append(self.get_expected_lambda())
        self.observation_history.append(observations.copy())

        return self.posterior_alpha, self.posterior_beta

    def get_expected_lambda(self) -> float:
        """
        Calculate the expected value of lambda from the current posterior.

        For Gamma(α, β), E[λ] = α/β

        Returns:
            Expected value of lambda
        """
        if self.posterior_beta > 0:
            return self.posterior_alpha / self.posterior_beta
        return self.alpha / self.beta

    def get_posterior_distribution(self):
        """
        Get the current posterior distribution parameters.

        Returns:
            Dictionary with posterior parameters
        """
        return {
            'alpha': self.posterior_alpha,
            'beta': self.posterior_beta,
            'expected_lambda': self.get_expected_lambda()
        }

    def sample_lambda(self, size: int = 1) -> np.ndarray:
        """
        Sample from the posterior distribution of lambda.

        Args:
            size: Number of samples to draw

        Returns:
            Array of sampled lambda values
        """
        return stats.gamma.rvs(self.posterior_alpha, scale=1/self.posterior_beta, size=size)

    def plot_distributions(self, num_samples: int = 10000, save_path: str = None):
        """
        Plot prior and posterior distributions of lambda.

        Args:
            num_samples: Number of samples for histogram
            save_path: Optional path to save the plot
        """
        # Generate samples
        prior_samples = stats.gamma.rvs(self.alpha, scale=1/self.beta, size=num_samples)
        posterior_samples = self.sample_lambda(num_samples)

        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Prior distribution
        ax1.hist(prior_samples, bins=50, density=True, alpha=0.7, color='blue')
        ax1.axvline(self.alpha / self.beta, color='red', linestyle='--',
                   label=f'E[λ] = {self.alpha/self.beta:.2f}')
        ax1.set_xlabel('λ')
        ax1.set_ylabel('Density')
        ax1.set_title('Prior Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Posterior distribution
        ax2.hist(posterior_samples, bins=50, density=True, alpha=0.7, color='green')
        ax2.axvline(self.get_expected_lambda(), color='red', linestyle='--',
                   label=f'E[λ] = {self.get_expected_lambda():.2f}')
        ax2.set_xlabel('λ')
        ax2.set_ylabel('Density')
        ax2.set_title('Posterior Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)

        plt.show()

    def get_probability_of_level(self, level: int) -> float:
        """
        Calculate the probability of observing a particular level
        under the current posterior distribution.

        Args:
            level: The level to calculate probability for

        Returns:
            Probability of observing that level
        """
        # For Poisson distribution with parameter lambda
        # P(X = k) = λ^k * e^(-λ) / k!
        lambda_val = self.get_expected_lambda()
        return stats.poisson.pmf(level, lambda_val)

    def get_log_likelihood(self, observations: np.ndarray) -> float:
        """
        Calculate the log likelihood of observations given current parameters.

        Args:
            observations: Array of observed student performance levels

        Returns:
            Log likelihood value
        """
        lambda_val = self.get_expected_lambda()
        return np.sum(stats.poisson.logpmf(observations, lambda_val))