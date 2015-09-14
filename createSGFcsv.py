import util.directory_tools as dt

dir = 'C:\AllProgrammingProjects\GoFamiliar\sgf_store\baduk-pro-collection'

with open('all_sgfs.csv', 'r'):

    for file in dt.search_tree(directory=dir, file_sig='*.sgf'):
        with open(file) as sgf_:
