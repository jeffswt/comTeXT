
class Trie:
    """Traversable dictionary tree."""

    class TrieNode:
        """Node for a dictionary tree."""

        def __init__(self, val, flag):
            self.key = val
            self.parent = None
            self.children = {}
            self.flag = flag
            return
        pass

    class TrieIterator:
        """Iterator object."""

        def __init__(self, trie):
            self.trie = trie
            self.gen = self.trie.traverse_tree()
            return

        def __next__(self):
            return next(self.gen)
        pass

    def __init__(self):
        self.root = self.TrieNode('', None)
        return

    def insert(self, string, flag):
        """Insert string into the dictionary.
        @param string(str) the string to insert
        @param flag(...) the object to mark upon discovery of the string"""
        p = self.root
        for i in range(0, len(string)):
            ch = string[i]
            if ch not in p.children:
                q = self.TrieNode(string[i], None)
                q.parent = p
                p.children[ch] = q
                p = q
            else:
                p = p.children[ch]
        p.flag = flag
        return

    def find(self, string):
        """Find if string exists in dictionary and return its flag.
        @param string(str) the string to search for
        @returns ... the flag of the string"""
        p = self.root
        for i in range(0, len(string)):
            ch = string[i]
            if ch not in p.children:
                return None
            p = p.children[ch]
        return p.flag

    def traverse_tree(self):
        """Creates a generator used to traverse all nodes."""
        # set default pointer
        p = self.root
        stack = [iter(p.children)]
        text = ''
        # traverse as stack
        while len(stack) > 0:
            i = stack[len(stack) - 1]
            # recurse if no children
            try:
                ch = next(i)
                p = p.children[ch]
                text += ch
                i = iter(p.children)
                stack.append(i)
            except StopIteration:
                if p.flag is not None:
                    yield text
                p = p.parent
                text = text[:-1]
                stack.pop()
                continue
            pass
        # nothing else to traverse
        raise StopIteration

    def __iter__(self):
        """Implement iter(self)."""
        i = self.TrieIterator(self)
        return i

    def __contains__(self, key):
        """Return key in self."""
        return self.find(key) is not None

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]"""
        val = self.find(key)
        if val is None:
            raise KeyError(key)
        return val

    def __setitem__(self, key, value):
        """Set self[key] to value."""
        self.insert(key, value)
        return
    pass
