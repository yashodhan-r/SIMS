import numpy as np

rng = np.random.default_rng(seed=0)

'''

model generation code.

W1 = rng.normal(0, 1, (2, 64))
b1 = np.zeros((1, 64), dtype=np.float64)
W2 = rng.normal(0, 1/np.sqrt(32), (64, 64))
b2 = np.zeros((1, 64), dtype=np.float64)
W3 = rng.normal(0, 1/np.sqrt(32), (64, 3))
b3 = np.zeros((1, 3), dtype=np.float64)

np.savetxt("models/W1.csv", W1, delimiter=",", fmt="%.17g")
np.savetxt("models/b1.csv", b1, delimiter=",", fmt="%.17g")
np.savetxt("models/W2.csv", W2, delimiter=",", fmt="%.17g")
np.savetxt("models/b2.csv", b2, delimiter=",", fmt="%.17g")
np.savetxt("models/W3.csv", W3, delimiter=",", fmt="%.17g")
np.savetxt("models/b3.csv", b3, delimiter=",", fmt="%.17g")
'''

W1 = np.loadtxt("models/working_model/W1.csv", delimiter=",", dtype=np.float64)
b1 = np.loadtxt("models/working_model/b1.csv", delimiter=",", dtype=np.float64)
W2 = np.loadtxt("models/working_model/W2.csv", delimiter=",", dtype=np.float64)
b2 = np.loadtxt("models/working_model/b2.csv", delimiter=",", dtype=np.float64)
W3 = np.loadtxt("models/working_model/W3.csv", delimiter=",", dtype=np.float64)
b3 = np.loadtxt("models/working_model/b3.csv", delimiter=",", dtype=np.float64)

projectile_data = np.array([[0.5, -0.8]])

def forward_pass(projectile_data):
    Z1 = projectile_data @ W1 + b1
    A1 = np.maximum(0, Z1)
    Z2 = A1 @ W2 + b2
    A2 = np.maximum(0, Z2)
    Z3 = A2 @ W3 + b3 # A2 (1x64)
    return [Z3, A2, Z2, A1, Z1]