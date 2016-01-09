"""Node object definition for tree construction. """

class Node:
    """Node object for tree construction.

    This construction can be found at http://cbio.ufs.ac.za/live_docs/nbn_tut/trees.html

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

        Error checks the children parameter ensuring it iterates over Node objects.

        :param value: Node value
        :param children: iterable over Node objects
        """
        if children is None:
            children = []

        try:
            for node in children:
                try:
                    assert type(node) == Node
                except AssertionError:
                    raise TypeError('Node expected. ' + str(type(node)) + ' received.')
        except TypeError:
            raise TypeError(str(children) + 'is not iterable')

        self.value = value
        self.children = list(children)

    def add(self, child):
        try:
            assert type(child) == Node
        except AssertionError:
            raise TypeError('Node expected. ' + str(type(child)) + ' received.')
        self.children.append(child)

