import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.size'] = 20

data1 = [
    (1, 62.570),
    (2, 63.318),
    (3, 80.379),
    (4, 133.460),
    (5, 224.964),
    (6, 483.631),
    (7, 510.662),
    (8, 338.267),
    (9, 185.721),
    (10, 109.889),
    (11, 85.891),
    (12, 72.331)
] # Kokchah




data2 = [ 
    (1, 699.242),
    (2, 648.465),
    (3, 803.987),
    (4, 1368.963),
    (5, 2264.350),
    (6, 3313.172),
    (7, 3982.143),
    (8, 2960.469),
    (9, 1630.676),
    (10, 927.233),
    (11, 808.265),
    (12, 769.903)
] # Amu Darya

data3 = [
    (1, 4626.667),
    (2, 4576.500),
    (3, 5768.867),
    (4, 10553.733),
    (5, 16941.467),
    (6, 29811.000),
    (7, 38509.500),
    (8, 40439.188),
    (9, 31213.533),
    (10, 20209.250),
    (11, 8678.938),
    (12, 5865.833)
] # Pandu 

data4 = [
    (1, 282.337),
    (2, 254.142),
    (3, 249.154),
    (4, 259.084),
    (5, 321.379),
    (6, 750.932),
    (7, 1737.857),
    (8, 3197.634),
    (9, 2179.327),
    (10, 902.776),
    (11, 512.646),
    (12, 350.195)
] # Yangcun

data5 = [
    (1, 18620.156),
    (2, 21103.981),
    (3, 20820.978),
    (4, 19301.316),
    (5, 17755.120),
    (6, 18000.480),
    (7, 16391.675),
    (8, 13927.393),
    (9, 13493.977),
    (10, 15448.656),
    (11, 15846.251),
    (12, 16315.080)
] #Parana

data6 = [
    (1, 222.507),
    (2, 198.135),
    (3, 205.257),
    (4, 1278.674),
    (5, 2417.891),
    (6, 2873.043),
    (7, 1986.087),
    (8, 1501.652),
    (9, 1102.087),
    (10, 872.957),
    (11, 509.000),
    (12, 275.587)
] # Ob



months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


fig, ax = plt.subplots(figsize=(11, 6))

# Plotting with log scale on the y-axis and using a new set of colors
colors = ['#1f78b4', '#33a02c', '#e31a1c', '#6a3d9a', '#ff7f00', '#a6cee3']


ax.hist([d[0] for d in data1], weights=[d[1] for d in data1], bins=12, histtype='step', fill=False, linewidth=3, label='Kokchah Khojaghar\n(Tajikistan)', color=colors[0])
ax.hist([d[0] for d in data2], weights=[d[1] for d in data2], bins=12, histtype='step', fill=False, linewidth=3, label='AmuDarya Kerki\n(Turkmenistan)', color=colors[1])
ax.hist([d[0] for d in data3], weights=[d[1] for d in data3], bins=12, histtype='step', fill=False, linewidth=3, label='Brahmaputra Pandu\n(India)', color=colors[2])
ax.hist([d[0] for d in data4], weights=[d[1] for d in data4], bins=12, histtype='step', fill=False, linewidth=3, label='Brahmaputra Yangcun\n(China)', color=colors[3])
ax.hist([d[0] for d in data5], weights=[d[1] for d in data5], bins=12, histtype='step', fill=False, linewidth=3, label='Parana Corrientes\n(Argentina)', color=colors[4])
ax.hist([d[0] for d in data6], weights=[d[1] for d in data6], bins=12, histtype='step', fill=False, linewidth=3, label='Ob Phominskoje\n(Russia)', color=colors[5])

# Set y-axis to log scale
ax.set_yscale('log')

# Set x-axis ticks and labels
ax.set_xticks(range(1, 13))
ax.set_xticklabels(months)

# Set x-axis and y-axis labels
ax.set_xlabel('Month')
ax.set_ylabel('Q ($m^3/s$)')

ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.set_title('Mean monthly discharge')


plt.show()