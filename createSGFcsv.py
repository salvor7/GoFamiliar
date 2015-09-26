import util.directory_tools as dt

dir = u'C:/AllProgrammingProjects/GoFamiliar/sgf_store/baduk-pro-collection'

with open('sgf_store/all_sgfs.csv', 'w', encoding='utf-8') as csv_file:
    files_found = dt.search_tree(directory=dir, file_sig='*.sgf')

    for file in files_found:
        with open(file, errors='replace', encoding='utf-8') as sgf_file:

            try:
                string = sgf_file.read()
            except:
                print(file)
                raise
            if 'SZ[19]' in string:
                csv_file.writelines(string.replace('\n', '') + '\n')