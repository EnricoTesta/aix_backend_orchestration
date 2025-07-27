from numpy import ones
from numpy.random import rand


class SpikeModel:
    def __init__(self, direction=1, intensity=0.05, sample_fraction=0.1):
        self.direction = direction  # 1 / -1
        self.intensity = intensity  # float
        self.sample_fraction = sample_fraction  # float [0, 1]
        self.n_class = None

    def fit(self, X, Y):
        self.n_class = len(Y.unique())
        return self

    def predict_proba(self, X):
        if self.n_class is None:
            raise ValueError("Call fit first!")

        # Generate baseline
        baseline = ones(X.shape[0]) / self.n_class

        # Sample indexes
        spike_indexes = rand(X.shape[0]) <= self.sample_fraction

        # Apply spikes
        return baseline + spike_indexes * self.direction * self.intensity
