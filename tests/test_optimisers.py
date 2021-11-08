'''
Testing the optimisers

Testing for function not performance see benchmarking script
'''
from freelunch.benchmarks import exponential
from freelunch import DE, SA, PSO, QPSO, SADE, KrillHerd, SA, GrenadeExplosion
import pytest
import numpy as np
import json
np.random.seed(100)


optimiser_classes = [SA, DE, PSO, QPSO, SADE, KrillHerd, GrenadeExplosion]
dims = [1, 2, 3]


def set_testing_hypers(opt):
    hypers = opt.hyper_defaults
    hypers['N'] = 5
    hypers['G'] = 2
    hypers['K'] = 2 # SA should really use G as well...
    hypers['Ng'] = 5
    hypers['Nq'] = 2
    return hypers


@pytest.mark.parametrize('opt', optimiser_classes)
def test_instancing_defaults(opt):
    o = opt()
    for k, v in o.hypers.items():
        if k in opt.hyper_defaults:
            assert np.all(v == opt.hyper_defaults[k])

# Since this happens in the base class it should be ok to just test DE


@pytest.mark.parametrize('n', [1, 3, 5])
def test_nfe(n):
    o = exponential(n)
    hypers = set_testing_hypers(DE)
    out = DE(obj=o, bounds=o.bounds, hypers=hypers)(nruns=n, full_output=True)
    assert out['nfe'] == (out['hypers']['G'] + 1) * out['hypers']['N'] * n


@pytest.mark.parametrize('opt', optimiser_classes)
@pytest.mark.parametrize('n', [1, 3])
@pytest.mark.parametrize('d', [1, 3, 5])
def test_run(opt, n, d):
    o = exponential(d)
    hypers = set_testing_hypers(opt)
    out = opt(obj=o, bounds=o.bounds, hypers=hypers)(nruns=n, full_output=True)
    assert(len(out['solutions']) == n*hypers['N'])
    # scores are ordered
    assert(all(x <= y for x, y in zip(out['scores'], out['scores'][1:])))
    for o in out['solutions']:
        for i, v in enumerate(o):
            assert(v > out['bounds'][i][0])
            assert(v < out['bounds'][i][1])


@pytest.mark.parametrize('opt', optimiser_classes)
@pytest.mark.parametrize('d', [1, 3, 5])
def test_run_one(opt, d):
    o = exponential(d)
    hypers = set_testing_hypers(opt)
    out = opt(obj=o, bounds=o.bounds, hypers=hypers)(full_output=True)
    assert(len(out['solutions']) == hypers['N'])


@pytest.mark.parametrize('opt', optimiser_classes)
@pytest.mark.parametrize('n', [1, 3])
@pytest.mark.parametrize('m', [1, 3])
@pytest.mark.parametrize('d', [1, 5])
def test_run_not_full(opt, n, m, d):
    o = exponential(d)
    hypers = set_testing_hypers(opt)
    out = opt(obj=o, bounds=o.bounds, hypers=hypers)(
        nruns=n, return_m=m, full_output=False)
    assert(len(out) == m)
    assert([(len(s) == d) for s in out])


@pytest.mark.parametrize('opt', optimiser_classes)
@pytest.mark.parametrize('n', [1, 3])
def test_can_json(opt, n):
    o = exponential(1)
    hypers = set_testing_hypers(opt)
    out = opt(obj=o, bounds=o.bounds, hypers=hypers)(nruns=n, full_output=True)
    s = json.dumps(out)


@pytest.mark.parametrize('opt', optimiser_classes)
def test_repr(opt):
    rep = opt().__repr__()
    assert(rep == (opt.name + ' optimisation object'))
