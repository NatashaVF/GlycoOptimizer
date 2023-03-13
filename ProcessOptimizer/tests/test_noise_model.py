from typing import List

import numpy as np
from ProcessOptimizer.model_systems.noise_models import NoiseModel, AdditiveNoise, MultiplicativeNoise, DataDependentNoise, ZeroNoise
from scipy.stats import norm
import pytest


@pytest.fixture
def signal_list():
    return [1,7,43,1212.21]

# If we are to fit the distributions, more data is needed
@pytest.fixture
def long_signal_list():
    return [1]*1000 + [10]*1000

# Setting the seed for the random number generator used so the tests are reproducible.
def setup_function():
    np.random.seed(42)

# Function for fitting a distribution and evaulating its mean and standard deviation.
def evaluate_random_dist(noise_list: List[float],size: float=1):
    (mean, spread) = norm.fit(noise_list)
    assert np.allclose(mean,0,atol=0.1*size)
    assert np.allclose(spread,size,atol=0.1*size)

def test_noise_abstract():
    # Tests that the abstract class can not be instantiated.
    with pytest.raises(TypeError):
        NoiseModel()

def test_additive_noise(signal_list):
    noise_model = AdditiveNoise(noise_dist=lambda: 2)
    noisy_list = [noise_model.apply(None,signal) for signal in signal_list]
    noise_list = [noise - signal for (signal,noise) in zip(signal_list, noisy_list)]
    assert all([noise == 2 for noise in noise_list])

@pytest.mark.parametrize("noise_level",(1,2,3))
def test_multiplicative_noise(signal_list, noise_level):
    noise_model = MultiplicativeNoise(noise_dist=lambda: noise_level)
    noisy_list = [noise_model.apply(None,signal) for signal in signal_list]
    noise_list = [noisy/signal-1 for (signal,noisy) in zip(signal_list, noisy_list)]
    assert np.allclose(noise_list,noise_level)

def test_multiplicative_noise_default(long_signal_list):
    noise_model = MultiplicativeNoise()
    noisy_list = [noise_model.apply(None,signal) for signal in long_signal_list]
    noise_list = [noisy/signal-1 for (signal,noisy) in zip(long_signal_list, noisy_list)]
    evaluate_random_dist(noise_list,0.01)

def test_multiplicative_noise_given_size(long_signal_list):
    noise_model = MultiplicativeNoise(noise_size = 0.1)
    noisy_list = [noise_model.apply(None,signal) for signal in long_signal_list]
    noise_list = [noisy/signal-1 for (signal,noisy) in zip(long_signal_list, noisy_list)]
    evaluate_random_dist(noise_list,0.1)

def test_random_noise(long_signal_list):
    noise_model = AdditiveNoise()
    noise_list = [noise_model.apply(None,signal) - signal for signal in long_signal_list]
    evaluate_random_dist(noise_list)

@pytest.mark.parametrize("size",(1,2,47))
def test_noise_size_additive(size, long_signal_list):
    noise_model = AdditiveNoise(noise_size=size)
    noise_list = [noise_model.apply(None,signal) - signal for signal in long_signal_list]
    evaluate_random_dist(noise_list,size)

@pytest.mark.parametrize("size",(1,2,47))
def test_noise_size_multiplicative(size, long_signal_list):
    noise_model = MultiplicativeNoise(noise_size=size)
    evaluate_random_dist(rel_noise_list,size)

@pytest.mark.parametrize("input",(1,2,3))
def test_data_dependent_noise(signal_list, input):
    # noice_choice returns a noice model that gives the same noise as the input data
    noise_choice = lambda X: AdditiveNoise(noise_dist = lambda: X)
    noise_model = DataDependentNoise(noise_models=noise_choice)
    noisy_list = [noise_model.apply(input,signal) for signal in signal_list]
    assert [noisy==input + signal for (signal,noisy) in zip(signal_list,noisy_list)]

def test_zero_noice(signal_list):
    noise_model = ZeroNoise()
    noisy_list = [noise_model.apply(None,signal) for signal in signal_list]
    assert [noisy==signal for (signal,noisy) in zip(signal_list,noisy_list)]

# Testing that the examples in the docstring of DataDependentNoise work
@pytest.mark.parametrize("magnitude",(1,2,3))
def test_noise_model_example_1(long_signal_list, magnitude):
    # the following two lines are taken from the docstring of DataDependentNoise
    noise_choice = lambda X: AdditiveNoise(noise_size=X)
    noise_model = DataDependentNoise(noise_models=noise_choice)
    data = [magnitude]*len(long_signal_list)
    noise_list = [noise_model.apply(x,signal) - signal for (x,signal) in zip(data,long_signal_list)]
    evaluate_random_dist(noise_list,magnitude)

def test_noise_model_example_2(long_signal_list):
    # the following two lines are taken from the docstring of DataDependentNoise
    noise_choice = lambda X: ZeroNoise() if X[0]==0 else AdditiveNoise()
    noise_model = DataDependentNoise(noise_models=noise_choice)
    X=[0,10,5]
    noise_list = [noise_model.apply(X,signal) - signal for signal in long_signal_list]
    (mean, spread) = norm.fit(noise_list)
    # This yields the zero noise model, where the fitted parameters are exactly zero
    assert mean==0
    assert spread==0
    X=[1,27,53.4]
    noise_list = [noise_model.apply(X,signal) - signal for signal in long_signal_list]
    evaluate_random_dist(noise_list)