import string
import re
from collections import Counter
import editdistance
import numpy as np
import nltk

class Autocorrection(object):

    def __init__(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            word = []
            lines = file.readlines()
            for line in lines:
                word += re.findall(r'\w+', line.lower())

        self.vocabulary = set(word)
        self.counts_of_word = Counter(word)
        self.total_words = float(sum(self.counts_of_word.values()))
        self.prob_of_word = {w: self.counts_of_word[w] / self.total_words for w in self.counts_of_word.keys()}

        # Build bigram counts and probabilities
        self.bigrams = list(nltk.bigrams(word))
        self.counts_of_bigram = Counter(self.bigrams)
        self.total_bigrams = float(sum(self.counts_of_bigram.values()))
        self.prob_of_bigram = {bg: self.counts_of_bigram[bg] / self.total_bigrams for bg in self.counts_of_bigram.keys()}

    def edit1(self, word):
        letter = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        insert = [l + c + r for l, r in splits for c in letter]
        delete = [l + r[1:] for l,r in splits if r]
        replace = [l + c + r[1:] for l, r in splits if r for c in letter]
        swap = [l + r[1] + r[0] + r[2:] for l, r in splits if len(r) > 1]

        return set(replace + insert + delete + swap)
  
    def edit2(self, word):
        return [e2 for e1 in self.edit1(word) for e2 in self.edit1(e1)]

    def common_prefix_length(self, word1, word2):
        # Calculating the length of the common prefix between two words
        common_len = 0
        for i, (c1, c2) in enumerate(zip(word1, word2)):
            if c1 == c2:
                common_len += 1
            else:
                break
        return common_len

    def custom_score(self, suggestion, original_word):
        # Assign weights to different edit operations (replace, insert, delete, swap)
        replace_weight = 1
        insert_weight = 2
        delete_weight = 3
        swap_weight = 4

        # Calculate the edit distance for each suggestion
        distance = editdistance.eval(suggestion, original_word)

        # Calculating a custom score based on the edit distance and the edit operation
        if len(suggestion) == len(original_word):  # Replace
            common_prefix_len = self.common_prefix_length(suggestion, original_word)
            score = distance * replace_weight + (len(original_word) - common_prefix_len)
        elif len(suggestion) == len(original_word) + 1:  # Insert
            common_prefix_len = self.common_prefix_length(suggestion, original_word)
            score = distance * insert_weight + (len(original_word) - common_prefix_len)
        elif len(suggestion) == len(original_word) - 1:  # Delete
            score = distance * delete_weight
        else:  # Swap
            score = distance * swap_weight

        return score
    


    def combined_score(self, suggestion, original_word):
        edit_score = self.custom_score(suggestion, original_word)
        prob_score = -np.log(self.prob_of_word.get(suggestion, 1e-9))  # Avoid log(0)
        return edit_score + prob_score

    
  
    def correct_spelling(self, word):
        if word in self.vocabulary:
            print(f"{word} is already correctly spelt")
            return

        ## suggestions = self.edit1(word) or self.edit2(word) or [word]
        suggestions = self.edit1(word).union(self.edit2(word))
        best_guesses = [w for w in suggestions if w in self.vocabulary]
        if not best_guesses:
            return[(word,0,0)]

        # Sorting the best guesses based on custom scoring
        best_guesses.sort(key=lambda w: self.combined_score(w, word))

        return [(w, self.prob_of_word[w]) for w in best_guesses]
        
    def correct_spelling_with_context(self, previous_word, word):
        """
        Suggest corrections for 'word' using the previous word as context (bigram probability).
        """
        if word in self.vocabulary:
            return [(word, self.prob_of_word[word], self.prob_of_bigram.get((previous_word, word), 0))]

        suggestions = self.edit1(word).union(self.edit2(word))
        best_guesses = [w for w in suggestions if w in self.vocabulary]
        if not best_guesses:
            return [(word, 0, 0)]

        # Sort by combined score: edit distance + unigram prob + bigram prob (if available)
        def context_score(w):
            edit_score = self.combined_score(w, word)
            unigram_score = -np.log(self.prob_of_word.get(w, 1e-9))
            bigram_score = -np.log(self.prob_of_bigram.get((previous_word, w), 1e-9)) if previous_word else 0
            return edit_score + unigram_score + 10*bigram_score

        best_guesses.sort(key=context_score)
        return [(w, self.prob_of_word[w], self.prob_of_bigram.get((previous_word, w), 0)) for w in best_guesses]
        