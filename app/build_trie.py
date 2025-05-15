import pickle
from graphviz import Digraph
import re
import os


# ------------------ TRIE NODE & TRIE ------------------ #
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def is_word_spelled_correctly(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def suggest_words(self, prefix, top_k=10):
        suggestions = []
        node = self.root

        for char in prefix:
            if char in node.children:
                node = node.children[char]
            else:
                return []

        def collect_words(node, current_word):
            if node.is_end_of_word:
                suggestions.append(current_word)
            for char, child in node.children.items():
                collect_words(child, current_word + char)

        collect_words(node, prefix)
        return suggestions[:top_k]

    def visualize(self, filename="trie", view=True):
        dot = Digraph(comment="Trie", format="pdf")
        dot.attr("node", shape="circle", style="filled", fontname="Noto Sans Devanagari")

        def add_nodes_edges(node, prefix=""):
            node_id = prefix or "ROOT"
            label = prefix if node.is_end_of_word else prefix or "ROOT"
            color = "lightgreen" if node.is_end_of_word else "lightblue"
            dot.node(node_id, label=label, fillcolor=color)

            for char, child in node.children.items():
                child_prefix = prefix + char
                add_nodes_edges(child, child_prefix)
                dot.edge(node_id, child_prefix, label=char)

        add_nodes_edges(self.root)
        dot.render(filename, view=view)
        print(f"Trie visualization written to {filename}.pdf")


# ------------------ HELPER FUNCTIONS ------------------ #
# Regex to match only Nepali characters (Devanagari block)
nepali_word_re = re.compile(r'^[\u0900-\u097F]+$')

def build_trie_from_file(file_path):
    trie = Trie()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                # Split on any whitespace and take the first part
                word = line.strip().split()[0] if line.strip() else ""
                if nepali_word_re.match(word):
                    trie.insert(word)
                if line_num % 100000 == 0:
                    print(f"Processed {line_num} lines...")
        print(f"Trie built from file with {line_num} lines processed.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    return trie


def save_trie(trie, filename="nepali_words_trie.pkl"):
    try:
        with open(filename, "wb") as f:
            pickle.dump(trie, f)
        print(f"Trie saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving trie: {e}")
        return False


def load_trie(filename="nepali_words_trie.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error loading trie: {e}")
        return None


def add_words_to_trie(new_words, filename="nepali_words_trie.pkl", save_and_visualize=True):
    trie = load_trie(filename)
    if trie is None:
        print("Could not load trie. Creating a new one.")
        trie = Trie()

    added_count = 0
    for word in new_words:
        word = word.strip()
        if word and nepali_word_re.match(word):
            if not trie.is_word_spelled_correctly(word):
                trie.insert(word)
                added_count += 1

    if save_and_visualize:
        if save_trie(trie, filename):
            try:
                trie.visualize("nepali_trie_updated", view=False)
            except Exception as e:
                print(f"Error visualizing trie: {e}")
    print(f"Added {added_count} new words to the Trie.")
    return trie


def add_words_from_file(file_path, filename="nepali_words_trie.pkl"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            words = [line.strip().split()[0] for line in f if line.strip()]
        return add_words_to_trie(words, filename)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None


# ------------------ MAIN SCRIPT ------------------ #

if __name__ == "__main__":
    vocab_file = "./data/vocab.txt"

    if os.path.exists(vocab_file):
        trie = build_trie_from_file(vocab_file)
        if trie is not None:
            save_success = save_trie(trie, "nepali_words_trie.pkl")
            if save_success:
                try:
                    trie.visualize(filename="nepali_trie", view=True)
                except Exception as e:
                    print(f"Error visualizing trie: {e}")
    else:
        print(f"Vocabulary file '{vocab_file}' not found. Using empty trie.")
        trie = Trie()

    # Test the loaded trie
    loaded_trie = load_trie("nepali_words_trie.pkl")
    if loaded_trie is None:
        loaded_trie = Trie()

    test_word = "काठमाडौं"
    if loaded_trie.is_word_spelled_correctly(test_word):
        print(f"'{test_word}' is spelled correctly.")
    else:
        print(f"'{test_word}' not found.")
        suggestions = loaded_trie.suggest_words(test_word[:2])
        print("Suggestions:", suggestions)

    # Example of adding new words
    new_words = ["काठमाडौं", "पोखरा", "भक्तपुर"]
    add_words_to_trie(new_words)
