
def init_projectors(self):
for i in range(0, self.N, 1):
    basis = np.zeros((self.N, 1))
    basis[i] = 1
    proj = basis @ basis.T
    self.projectors.append(proj)

'''@param
state = The entire quantum state
i = which qudit to measure
j = the basis state
'''
def project(self, i, j):
projected = np.tensordot(self.projectors[j], self.psi, (1,i))
return np.moveaxis(projected, 0, i)

#measure the 'i'th qudit in n basis
#return probability and posterior states
def measure(self, i):
basis_states = np.arange(0, self.N)
probs = []
projections = []

for b in range(self.N):
    projected = self.project(i, b)
    projections.append(projected)
    norm_projected = norm(projected.flatten()) 
    probs.append(norm_projected**2)

print("Probabilities = ", probs)

found_in_basis = np.random.choice(basis_states, 1, p=probs)[0]
#projected = self.project(i, b)
self.psi = projections[found_in_basis] / np.sqrt(probs[found_in_basis])
return found_in_basis, probs[found_in_basis]

def measure_all_possible_posteriors(self, i):
basis_states = np.arange(0, self.N)
probs = []
projections = []

for b in range(self.N):
    projected = self.project(i, b)
    projections.append(projected)
    norm_projected = norm(projected.flatten()) 
    probs.append(norm_projected**2)

for b in basis_states:
    #tuple of state, probability
    self.all_possible_posteriors.append((projections[b] / np.sqrt(probs[b]), probs[b]))

return self.all_possible_posteriors