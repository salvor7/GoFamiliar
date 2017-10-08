"""Node object definition for tree construction. """

class Node(object):
    """Node object for tree construction.

    This construction can be found at http://cbio.ufs.ac.za/live_docs/nbn_tut/trees.html

    >>> tree = Node(rel0='grandmother',
    ...             children=[Node(rel1='daughter',
    ...                              children=[ Node(rel2='granddaughter'),
    ...                                         Node(rel2='grandson')]
    ...                             ),
    ...                       Node(rel1='son',
    ...                             children=[ Node(rel2='granddaughter'),
    ...                                        Node(rel2='grandson')]
    ...                 )])
    >>> tree.rel0
    'grandmother'
    >>> tree.children[0].rel1
    'daughter'
    >>> tree.children[0].children[0].rel2
    'granddaughter'
    """
    def __init__(self, children=None, **kwargs):
        """
        Construct a Node.

        Error checks the children parameter ensuring it iterates over Node objects.
        :param children: iterable over Node objects
        """
        if children is None:
            children = []
        self.children = []
        for child in children:
            self.add(child)

        for keyword, value in kwargs.items():
            setattr(self, keyword, value)

        self.parent = None

    def add(self, child):
        """
        Add a child

        :param child: Node
        """
        try:
            assert type(child) == Node
        except AssertionError:
            raise TypeError('Node expected. ' + str(type(child)) + ' received.')
        child.parent = self
        self.children.append(child)
