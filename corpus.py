import pickle
import math
from collections import Counter

from preprocessing import preprocess


class Corpus:
    """Class to compute and store various bag-of-words statistics for
    a corpus of text documents.

    doc_freqs (Counter): Counter that maps a word to the total number of
    docs the word occurs in.
    global_tf (Counter): Counter that maps a word to the total number of
    occurrences of a word across a corpus.
    doc_tfs (dictionary): Dictionary mapping indices for docs to a counter
    for word frequencies within that doc.
    importance (dictionary): Dictionary mapping each word to an 'importance' or
    'information content' value.
    most_common_freq (dictionary): Dictionary mapping doc indices to the
    highest word frequency found in that doc used for double-normalization of
    term freq).
    docs (dictionary): Dictionary mapping indices for a doc to the original
    doc.

    Note: importance(word) = log(global_tf[word]) / doc_freqs[word]
    """

    def __init__(self, texts=None):
        """Initializes variables for self.

        Parameter:
        texts (iterable): A corpus (iterable of strings).
        """
        self.doc_freqs = Counter()
        self.global_tf = Counter()
        self.doc_tfs = dict()
        self.importance = dict()
        if not texts:
            self.docs = dict()
            return
        self.docs = dict(enumerate(texts))
        for i, text in self.docs.items():
            tokens = preprocess(text)
            self.global_tf.update(tokens)
            self.doc_tfs[i] = Counter(tokens)
            self.doc_freqs.update(set(tokens))
        self.compute_importance()

    def __get__(self, word):
        """Finds the importance of word.

        Parameter:
        word (str): Word to find importance of.

        Return:
        (float): Importance value for word.

        Note: importance(word) = log(global_tf[word]) / doc_freqs[word]
        """
        return self.get_importance(word)

    def compute_importance(self):
        """Computes importance values for each word in doc_freqs.

        Note: importance(word) = log(global_tf[word]) / doc_freqs[word]
        """
        for word, doc_freq in self.doc_freqs.items():
            word_freq = self.global_tf.get(word, 0)
            if word_freq > 0:
                word_freq = math.log(word_freq)
            self.importance[word] = float(word_freq) / doc_freq

    def get_importance(self, word):
        """Finds the importance of word.

        Parameter:
        word (str): Word to find importance of.

        Return:
        (float): Importance value for word.

        Note: importance(word) = log(global_tf[word]) / doc_freqs[word]
        """
        if len(self.importance) == 0:
            self.compute_importance()
        return self.importance.get(word, 0)

    def get_global_tf(self, word):
        """Returns the global count of word.

        Return:
        (int): Number of times word occurs in all docs.
        """
        return self.global_tf.get(word, 0)

    def get_tf(self, doc_id, word):
        """Returns the count of word in the specified doc if the doc exists
        in the corpus and the word exists in the doc.

        Parameters:
        doc_id (int): Indice of doc you are trying to get a counter from.
        word (str): Word you are trying to get a count of.

        Return:
        (int): Number of occurrences of word in the doc that doc_id belongs to.
        """
        doc_tf_counter = self.doc_tfs.get(doc_id, None)
        return None if doc_tf_counter is None else doc_tf_counter.get(word, 0)

    def get_ntf(self, doc_id, word, k=0.4):
        """Computes the double normalized term frequency of word in doc_id.

        Parameters:
        doc_id (int): Indice of doc you are trying to get a word counter from.
        word (str): Word you are trying to get a double normalized frequency of.

        Return:
        ntf (float): Double normalized frequency of word in doc_id.
        """
        doc_tf = self.doc_tfs.get(doc_id, Counter())
        if not doc_tf:
            return 0
        highest_freq = max(doc_tf.values())
        if not highest_freq:
            return 0
        word_freq = doc_tf.get(word, 0)
        ntf = k + (1.0 - k) * word_freq / highest_freq
        return ntf

    def save_vocab(self, fname):
        """Saves vocab from corpus into a binary file.

        Parameter:
        fname (str): Name of file to save vocab to.
        """
        vocab = self.idf.keys()
        with open(fname, "wb") as f:
            pickle.dump(vocab, f)
