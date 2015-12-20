def test_sgf_parser():
    """
    >>> basic_branching2 = '(;SZ[19];B[jj];W[kl](;B[dd](;W[gh])   (;W[sa]))(;B[cd]))'
    >>> sgf_parser(basic_branching2)
    ['SZ[19]', 'B[jj]', 'W[kl]', ['B[dd]', ['W[gh]'], ['W[sa]']], ['B[cd]']]
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp]) (;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])  (;W[pd]))'
    ...                 '(;B[oq];W[dd]))')
    >>> for chunk in sgf_parser(complex_branching):
    ...    chunk
    'RU[Japanese]'
    'SZ[19]'
    'KM[6.50]'
    'B[jj]'
    'W[kl]'
    ['B[pd]', ['W[pp]'], ['W[dc]', ['B[de]'], ['B[dp]']]]
    ['B[cd]', 'W[dp]']
    ['B[cq]', ['W[pq]'], ['W[pd]']]
    ['B[oq]', 'W[dd]']
    """
    pass

def test_main_branch():
    """

    >>> linear_sgf = '(;KM[2.75]SZ[19];B[qd];W[dd];B[oc];W[pp];B[do];W[dq])'
    >>> sgf_parser(linear_sgf) == sgf_main_branch(sgf_parser(linear_sgf))
    True
    >>> complex_branching = ('(;RU[Japanese]SZ[19]KM[6.50];B[jj];W[kl]'
    ...                 '(;B[pd](;W[pp])(;W[dc](;B[de])(;B[dp])))'
    ...                 '(;B[cd];W[dp])'
    ...                 '(;B[cq](;W[pq])(;W[pd]))'
    ...                 '(;B[oq];W[dd]))')
    >>> sgf_main_branch(sgf_parser(complex_branching))
    ['RU[Japanese]', 'SZ[19]', 'KM[6.50]', 'B[jj]', 'W[kl]', 'B[pd]', 'W[pp]']
    """
    pass

def test_node_to_move():
    """
    >>> try:
    ...     node_to_move('error')
    ... except ValueError as err:
    ...     print(err)
    "error" is not a sgf move formatted node
    """
    pass