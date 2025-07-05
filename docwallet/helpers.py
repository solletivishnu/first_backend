from collections import defaultdict


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.words = []

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        word = word.lower()
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            if word not in node.words:
                node.words.append(word)
        node.is_end_of_word = True

    def search_prefix(self, prefix, limit=10):
        prefix = prefix.lower()
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return node.words[:limit]


# utils/context_tries.py


context_tries = defaultdict(Trie)

def build_context_tries():
    from .models import Document
    context_tries.clear()
    all_docs = Document.objects.select_related('folder__wallet__context')

    for doc in all_docs:
        context_id = doc.folder.wallet.context_id
        context_tries[context_id].insert(doc.name)
