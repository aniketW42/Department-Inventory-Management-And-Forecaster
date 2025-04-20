import matplotlib.pyplot as plt

# Class intervals and frequencies
class_intervals = [(1400,1600), (1600,1800), (1800,2000), (2000,2200), (2200,2400), (2400,2600)]
frequencies = [12, 30, 55, 40, 35, 28]

# Calculate upper class boundaries and cumulative frequencies
upper_bounds = [interval[1] for interval in class_intervals]
cumulative_frequencies = []

cumulative = 0
for f in frequencies:
    cumulative += f
    cumulative_frequencies.append(cumulative)

# Plotting the ogive
plt.figure(figsize=(10, 6))
plt.plot(upper_bounds, cumulative_frequencies, marker='o', linestyle='-', color='blue')
plt.title('Less Than Ogive (Cumulative Frequency Curve)')
plt.xlabel('Monthly Salary (Upper Bound in Rs.)')
plt.ylabel('Cumulative Frequency')
plt.grid(True)

# Highlighting the median line
N = cumulative_frequencies[-1]
median_y = N / 2

plt.axhline(y=median_y, color='red', linestyle='--', label='N/2 = {}'.format(median_y))
# Estimate x at median_y visually from the graph
plt.legend()
plt.show()
