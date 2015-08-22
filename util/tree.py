
class Node:
    """Construct can be found at http://cbio.ufs.ac.za/live_docs/nbn_tut/trees.html

    >>> tree = Node('grandmother', [
    ...                             Node('daughter', [ Node('granddaughter'), Node('grandson')]),
    ...                             Node('son', [ Node('granddaughter'), Node('grandson')])
    ...                             ])
    >>> tree.value
    'grandmother'
    >>> tree.children[0].value
    'daughter'
    >>> tree.children[0].children[0].value
    'granddaughter'

    """
    def __init__(self, value, children = None):
        """Construct a Node.

        :param value: Node value
        :param children: [Nodes]
        """
        self.value = value
        self.children = children

if __name__ == '__main__':
    import doctest
    doctest.testmod()