
import re


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
        return self.data[key]

    def has_parent(self):
        """has_parent()
        @returns bool True if has parent"""
        return self.parent is not None

    def has_children(self):
        """has_children()
        @returns bool True if has children"""
        return len(self.children) > 0

    def is_parent(self, node):
        """is_parent(node)
        @param node(DOMObject) the node to check on
        @returns bool True if node is self's parent"""
        return self.parent == node and self in node.children

    def is_child(self, node):
        """is_child(node)
        @param node(DOMObject) the node to check on
        @returns bool True if node is self's child"""
        return node.parent == self and node in self.children

    def insert_child(self, node, index):
        """insert_child(node, index) -- insert node before index
            behavior resembles that of list.insert(...)
        @param node(DOMObject) the node to insert
        @param index(int) position of node after insertion
        @returns None"""
        if not node.has_parent():
            raise DOMError('target node has parent')
        self.children.insert(node, index)
        node.parent = self
        return

    def prepend_child(self, node):
        """prepend_child(node) -- insert node at the begin of its children
        @param node(DOMObject) the node to prepend
        @returns None"""
        return self.insert_child(node, 0)

    def append_child(self, node):
        """append_child(node) -- insert node at the end of its children
        @param node(DOMObject) the node to append
        @returns None"""
        if not node.has_parent():
            raise DOMError('target node has parent')
        self.children.append(node)
        node.parent = self
        return

    def get_string(self):
        """get_string() -- get string representation of this node
        @returns str output"""
        res = ''
        for i in self.children:
            res += i.get_string()
        return res
    pass


class DOMString(DOMObject):
    """Single line object, should not contain line breaks."""

    def __init__(self, data):
        DOMObject.__init__()
        self.data['string'] = data
        return

    def get_string(self):
        return self.data['string']
    pass


class DOMLineBreak(DOMObject):
    """Single line break."""

    def get_string(self):
        return '\n'
    pass
