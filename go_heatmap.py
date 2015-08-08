from bokeh.charts import HeatMap, show, output_file
from bokeh.palettes import Spectral11 as palette


def make_heatmap(counts_df, file_name='ghm.html'):

    output_file(file_name)
    show(HeatMap(counts_df, palette=palette))


# DO LATER find if colours can be transparent
# DO LATER find if a background png can be added to the display ie a goban
# DO LATER create a user defined palettes
# DO LATER pixelate the heatmap     pixels = 7

# DO LATER test how updating works

