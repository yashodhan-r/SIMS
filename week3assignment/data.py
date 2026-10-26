import numpy as np

rng = np.random.default_rng(seed=0)

velocity = rng.uniform(low=5.0, high=50.0, size=(2000))
angles_deg = rng.uniform(low=5, high=85, size=(2000))
angles_rad = np.radians(angles_deg)

range = (velocity ** 2) * np.sin(2 * angles_rad) / 9.81
time = (2 * velocity * np.sin(angles_rad)) / 9.81
height = (velocity ** 2) * (np.sin(angles_rad) ** 2) / (2 * 9.81)


#np.savez_compressed("dataset.npz", velocity = velocity, angles_deg = angles_deg, range = range, time = time, height = height)

permutationOrder = rng.permutation(2000)

input_training = np.column_stack((velocity[permutationOrder[0:1400]], angles_deg[permutationOrder[0:1400]]))
output_training = np.column_stack((range[permutationOrder[0:1400]], time[permutationOrder[0:1400]], height[permutationOrder[0:1400]]))

input_testing = np.column_stack((velocity[permutationOrder[1400:1700]], angles_deg[permutationOrder[1400:1700]]))
output_testing = np.column_stack((range[permutationOrder[1400:1700]], time[permutationOrder[1400:1700]], height[permutationOrder[1400:1700]]))

input_validation = np.column_stack((velocity[permutationOrder[1700:2000]], angles_deg[permutationOrder[1700:2000]]))
output_validation = np.column_stack((range[permutationOrder[1700:2000]], time[permutationOrder[1700:2000]], height[permutationOrder[1700:2000]]))

velocity_mean_train = input_training[:, 0].mean()
angles_mean_train = input_training[:, 1].mean()

velocity_std_train = input_training[:, 0].std()
angles_std_train = input_training[:, 1].std()

input_training_zscored = np.column_stack(((input_training[:, 0] - velocity_mean_train) / velocity_std_train,(input_training[:, 1] - angles_mean_train) / angles_std_train))
input_testing_zscored = np.column_stack(((input_testing[:, 0] - velocity_mean_train) / velocity_std_train,(input_testing[:, 1] - angles_mean_train) / angles_std_train))
input_validation_zscored = np.column_stack(((input_validation[:, 0] - velocity_mean_train) / velocity_std_train,(input_validation[:, 1] - angles_mean_train) / angles_std_train))

np.savetxt("training_data/inputtraining.csv", input_training_zscored, delimiter=",", fmt="%.17g")
np.savetxt("training_data/inputtesting.csv", input_testing_zscored, delimiter=",", fmt="%.17g")
np.savetxt("training_data/inputvalidation.csv", input_validation_zscored, delimiter=",", fmt="%.17g")

range_mean = output_training[:, 0].mean()
time_mean = output_training[:, 1].mean()
height_mean = output_training[:, 2].mean()
mean = np.array([range_mean, time_mean, height_mean])

range_std = output_training[:, 0].std()
time_std = output_training[:, 1].std()
height_std = output_training[:, 2].std()

sd = np.array([range_std, time_std, height_std])

output_training_zscored = (output_training - mean)/sd
output_testing_zscored = (output_testing - mean)/sd
output_validation_zscored = (output_validation - mean)/sd

np.savetxt("training_data/outputtraining.csv", output_training_zscored, delimiter=",", fmt="%.17g")
np.savetxt("training_data/outputtesting.csv", output_testing_zscored, delimiter=",", fmt="%.17g")
np.savetxt("training_data/outputvalidation.csv", output_validation_zscored, delimiter=",", fmt="%.17g")

np.savetxt("training_data/normalization_data.csv", np.column_stack((velocity_mean_train, angles_mean_train, velocity_std_train, angles_std_train, range_mean, time_mean, height_mean, range_std, time_std, height_std)), delimiter=",", fmt="%.17g")


