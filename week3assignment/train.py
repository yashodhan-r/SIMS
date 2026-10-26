import numpy as np
import model

input_training = np.loadtxt("training_data/inputtraining.csv", delimiter=",", dtype=np.float64) # 1400x2 array of velocity and angle values. 
output_training = np.loadtxt("training_data/outputtraining.csv", delimiter=",", dtype=np.float64) # 1400x3 array of range, time, and height values.


def backpass(data_row):
    run_forwardpass = model.forward_pass(input_training[data_row:data_row+1,0:2]) # <--Z3, A2, Z2, A1, Z1

    temp = run_forwardpass[0]-output_training[data_row:data_row+1,0:3] # <--Z3... (1,3)
    Loss = np.sum(temp**2)

    G3 = 2*temp # contains delL/delR,H,T so you multiply that by delE,H,T/delW3 ....  delR,T,H/delb3 is always 1 cuz b3 is like constant ... aw + b
    gradient_b3 = G3
    gradient_w3 = run_forwardpass[1].T@G3 #A2 1x64 was taken and transposed to 64x1 and multiplied with G3 (1x3) - 64x3 gradient... 64x4 is also W3's size

    G2 = G3@model.W3.T # G3 (1x3) @ Z2.T (3x64) = 1x64
    G2[run_forwardpass[2] <= 0] = 0 # ReLU derivative
    gradient_b2 = G2
    gradient_w2 = run_forwardpass[3].T@G2 #A1 1x64 was taken and transposed to 64x1 and multiplied with G2 (1x64) - 64x64 gradient... 64x64 is also W2's size

    G1 = G2@model.W2.T # G2 (1x64) @ Z1.T (64x64) = 1x64
    G1[run_forwardpass[4] <= 0] = 0 # ReLU derivative
    gradient_b1 = G1
    gradient_w1 = input_training[data_row:data_row+1, 0:2].T @ G1 #A0 1x2 was taken and transposed to 2x1 and multiplied with G1 (1x64) - 2x64 gradient... 2x64 is also W1's size

    '''
    print(np.shape(gradient_w1))
    print(np.shape(gradient_w2))
    print(np.shape(gradient_w3))
    print(np.shape(gradient_b1))
    print(np.shape(gradient_b2))
    print(np.shape(gradient_b3))
    '''
    
    model.W1 = model.W1 - 0.0001*gradient_w1
    model.b1 = model.b1 - 0.0001*gradient_b1
    model.W2 = model.W2 - 0.0001*gradient_w2
    model.b2 = model.b2 - 0.0001*gradient_b2
    model.W3 = model.W3 - 0.0001*gradient_w3
    model.b3 = model.b3 - 0.0001*gradient_b3
    
    return Loss

arr = np.zeros((1000,3))

for epoch in range(1000):
    loss = 0
    loss_avg = 0
    for data_row in range(1400):
        loss = backpass(data_row)
        loss_avg += loss
    loss_avg /= 1400
    print("Epoch: ", epoch, " Loss: ", loss)
    arr[epoch,0] = epoch
    arr[epoch,1] = loss
    arr[epoch,2] = loss_avg # Assuming you want to store the loss in the third column as well
np.savetxt("analytics/3.0/epoch_vs_loss.csv", arr, delimiter=",", fmt="%.17g")
'''
np.savetxt("models/model_v3/W1.csv", model.W1, delimiter=",", fmt="%.17g")
np.savetxt("models/model_v3/b1.csv", model.b1, delimiter=",", fmt="%.17g")
np.savetxt("models/model_v3/W2.csv", model.W2, delimiter=",", fmt="%.17g")
np.savetxt("models/model_v3/b2.csv", model.b2, delimiter=",", fmt="%.17g")
np.savetxt("models/model_v3/W3.csv", model.W3, delimiter=",", fmt="%.17g")
np.savetxt("models/model_v3/b3.csv", model.b3, delimiter=",", fmt="%.17g")
'''

input_validation = np.loadtxt("training_data/inputvalidation.csv", delimiter=",", dtype=np.float64) # 300x2 array of velocity and angle values.
output_validation = np.loadtxt("training_data/outputvalidation.csv", delimiter=",", dtype=np.float64) # 300x3 array of range, time, and height values.

validation_loss = np.zeros((300,8))

for data_row in range(300):
    run_forwardpass = model.forward_pass(input_validation[data_row:data_row+1,0:2]) # <--Z3, A2, Z2, A1, Z1
    temp = run_forwardpass[0]-output_validation[data_row:data_row+1,0:3] # <--Z3... (1,3)
    Loss = np.sum(temp**2)
    validation_loss[data_row] = np.column_stack((input_validation[data_row:data_row+1,0:2], run_forwardpass[0], output_validation[data_row:data_row+1,0:3]))
    print("Validation Data Row: ", data_row, " Loss: ", Loss)
np.savetxt("analytics/3.0/RTH.csv", validation_loss, delimiter=",", fmt="%.17g")

training_loss = np.zeros((1400))
for data_row in range(1400):
    run_forwardpass = model.forward_pass(input_training[data_row:data_row+1,0:2]) # <--Z3, A2, Z2, A1, Z1
    temp = run_forwardpass[0]-output_training[data_row:data_row+1,0:3] # <--Z3... (1,3)
    Loss = np.sum(temp**2)
    training_loss[data_row] = Loss
    print("Training Data Row: ", data_row, " Loss: ", Loss)
np.savetxt("analytics/3.0/training_loss.csv", training_loss, delimiter=",", fmt="%.17g")
