__author__ = 'salvor7'
import sgf
import pandas
import os
import fnmatch

matches = []
for root, dirnames, filenames in os.walk(r'c:\AllProgrammingProjects\badukmovies-pro-collection'):
  for filename in fnmatch.filter(filenames, '*.sgf'):
    matches.append(filename)

print(os.path)
print(matches)