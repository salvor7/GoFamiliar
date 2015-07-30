from bokeh.charts import HeatMap, show, output_file
from bokeh.palettes import Spectral11 as palette


def make_heatmap(counts_df, file_name='ghm.html'):

    output_file(file_name)
    show(HeatMap(counts_df, palette=palette))


# TODO find if colours can be transparent
# TODO find if a background png can be added to the display ie a goban
# TODO create a user defined palettes
# TODO pixelate the heatmap     pixels = 7

# TODO test how updating works

