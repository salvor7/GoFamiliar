from bokeh.charts import HeatMap, output_file, show
import numpy as np



# (dict, OrderedDict, lists, arrays and DataFrames are valid inputs)
data = {'fruit': ['apples']*3 + ['bananas']*3 + ['pears']*3,
        'fruit_count': [4, 5, 8, 1, 2, 4, 6, 5, 4],
        'sample': [1, 2, 3]*3}

hm = HeatMap(data, x='fruit', y='sample', values='fruit_count',
             title='Fruits', stat=None)


show(hm)


ran_board = np.random.randint(low=1, high=100, size=19*19)
print(ran_board)


data = list(ran_board)

di = {'x_axis':['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']*19,
        'y_axis':[i for i in range(1,20)]*19,
        'heat':ran_board,
}

hm = HeatMap(data=data)

output_file('heatmap.html')
show(hm)