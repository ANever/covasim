'''
Compare simulating the entire population vs. dynamic rescaling vs. static rescaling.
'''

import sciris as sc
import covasim as cv

T = sc.tic()

p = sc.objdict() # Parameters
s = sc.objdict() # Sims
m = sc.objdict() # Multisims

# Interventions
iday = 30
cb = cv.change_beta(days=iday, changes=0.5) # Change beta
tn = cv.test_num(start_day=iday, daily_tests=1000, symp_test=10) # Test a number of people
tp = cv.test_prob(start_day=iday, symp_prob=0.1, asymp_prob=0.01) # Test a number of people

# Properties that are shared across sims
basepop      = 10e3
popinfected  = 20
popscale1    = 10
popscale2    = 20 # Try a different population scale
which_interv = 2 # Which intervention to test

shared = sc.objdict(
    n_days = 120,
    beta = 0.015,
    interventions = [cb, tn, tp][which_interv],
)

# Simulate the entire population
p.entire = dict(
    pop_size     = basepop*popscale1,
    pop_infected = popinfected,
    pop_scale    = 1,
    rescale      = False,
)

# Simulate a small population with dynamic scaling
p.rescale = dict(
    pop_size     = basepop,
    pop_infected = popinfected,
    pop_scale    = popscale1,
    rescale      = True,
)

# Simulate a small population with static scaling
p.static = dict(
    pop_size     = basepop,
    pop_infected = popinfected//popscale1,
    pop_scale    = popscale1,
    rescale      = False,
)

# Simulate an extra large population
p.entire2 = dict(
    pop_size     = basepop*popscale2,
    pop_infected = popinfected,
    pop_scale    = 1,
    rescale      = False,
)

# Simulate a small population with dynamic scaling
p.rescale2 = dict(
    pop_size     = basepop,
    pop_infected = popinfected,
    pop_scale    = popscale2,
    rescale      = True,
)

# Simulate a small population with static scaling
p.static2 = dict(
    pop_size     = basepop,
    pop_infected = popinfected//popscale2,
    pop_scale    = popscale2,
    rescale      = False,
)


# Create and run the sims
keys = p.keys()

for key in keys:
    p[key].update(shared)

for key in keys:
    s[key] = cv.Sim(pars=p[key], label=key)
    m[key] = cv.MultiSim(base_sim=s[key], n_runs=10)

for key in keys:
    m[key].run()
    m[key].reduce()


# Plot
to_plot = {
    'Totals': ['cum_infections', 'cum_tests', 'cum_diagnoses'],
    'New': ['new_infections', 'new_tests', 'new_diagnoses'],
    }

for key in keys:
    m[key].plot(to_plot=to_plot)

bsims = [msim.base_sim for msim in m.values()]
mm = cv.MultiSim(sims=bsims)
mm.compare()

sc.toc(T)