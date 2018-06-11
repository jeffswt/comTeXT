
class DOMError(RuntimeError):
    """Raised while performing an illegal operation on the DOM model"""
    pass


class DOMObject(object):
    """Document Object Model Object
    Serves as a node under the document."""

    def __init__(self):
        self.parent = None
        self.children = []
        self.data = {}
        return

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]"""
        return self.data[key]

    def has_parent(self):
        """Returns True if has parent.
        @returns bool True if has parent"""
        return self.parent is not None

    def has_children(self):
        """Returns True if has children.
        @returns bool True if has children"""
        return len(self.children) > 0

    def is_parent(self, node):
        """Returns True if self's parent is node.
        @param node(DOMObject) the node to check on
        @returns bool True if node is self's parent"""
        return self.parent == node and self in node.children

    def is_child(self, node):
        """Returns True if node is a child of self.
        @param node(DOMObject) the node to check on
        @returns bool True if node is self's child"""
        return node.parent == self and node in self.children

    def insert_child(self, node, index):
        """Insert node before index, resembles that of list.insert(...).
        @param node(DOMObject) the node to insert
        @param index(int) position of node after insertion
        @returns None"""
        if not node.has_parent():
            raise DOMError('target node has parent')
        self.children.insert(node, index)
        node.parent = self
        return

    def prepend_child(self, node):
        """Insert node at the begin of its children.
        @param node(DOMObject) the node to prepend
        @returns None"""
        return self.insert_child(node, 0)

    def append_child(self, node):
        """Insert node at the end of its children.
        @param node(DOMObject) the node to append
        @returns None"""
        if not node.has_parent():
            raise DOMError('target node has parent')
        self.children.append(node)
        node.parent = self
        return

    def get_string(self):
        """Get string representation of this node.
        @returns str output"""
        res = ''
        for i in self.children:
            res += i.get_string()
        return res
    pass


class DOMString(DOMObject):
    """String object without format. May contain line breaks."""

    def __init__(self, data):
        DOMObject.__init__()
        self.data['string'] = data
        return

    def get_string(self):
        return self.data['string']
    pass
