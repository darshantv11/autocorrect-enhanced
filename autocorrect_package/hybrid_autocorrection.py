import string
import re
from collections import Counter
import editdistance
import numpy as np
import nltk
from nltk.corpus import brown, reuters
import json
import os

class HybridAutocorrection(object):
    """
    Hybrid autocorrection system that intelligently combines original and enhanced approaches.
    """

    def __init__(self, original_corpus_file="autocorrect_package/corpus2.txt", use_large_corpora=True):
        self.use_large_corpora = use_large_corpora
        self.custom_words = set()
        self.user_feedback = {}
        
        # Load original corpus
        self.original_words = self.load_original_corpus(original_corpus_file)
        
        # Load large corpora if enabled
        if use_large_corpora:
            self.large_corpus_words = self.load_large_corpora()
            all_words = self.original_words + self.large_corpus_words
        else:
            all_words = self.original_words
        
        # Build vocabulary and statistics
        self.build_vocabulary(all_words)
        
        # Load custom words if they exist
        self.load_custom_words()
        
        print(f"Hybrid Autocorrection initialized with {len(self.vocabulary)} unique words")

    def load_original_corpus(self, filename):
        """Load words from the original corpus file."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                words = []
                lines = file.readlines()
                for line in lines:
                    words += re.findall(r'\w+', line.lower())
            return words
        except FileNotFoundError:
            print(f"Warning: {filename} not found, using only large corpora")
            return []

    def load_large_corpora(self):
        """Load words from Brown and Reuters corpora."""
        words = []
        
        try:
            print("Loading Brown corpus...")
            brown_words = brown.words()
            words.extend([word.lower() for word in brown_words if word.isalpha()])
            print(f"Loaded {len(brown_words)} words from Brown corpus")
            
        except Exception as e:
            print(f"Warning: Could not load Brown corpus: {e}")
        
        try:
            print("Loading Reuters corpus...")
            reuters_words = reuters.words()
            words.extend([word.lower() for word in reuters_words if word.isalpha()])
            print(f"Loaded {len(reuters_words)} words from Reuters corpus")
            
        except Exception as e:
            print(f"Warning: Could not load Reuters corpus: {e}")
        
        return words

    def build_vocabulary(self, all_words):
        """Build vocabulary, word counts, and n-gram models."""
        # Basic vocabulary and word counts
        self.vocabulary = set(all_words)
        self.counts_of_word = Counter(all_words)
        self.total_words = float(sum(self.counts_of_word.values()))
        self.prob_of_word = {w: self.counts_of_word[w] / self.total_words for w in self.counts_of_word.keys()}
        
        # Add custom words to vocabulary
        self.vocabulary.update(self.custom_words)
        
        # Build bigram model
        print("Building bigram model...")
        self.bigrams = list(nltk.bigrams(all_words))
        self.counts_of_bigram = Counter(self.bigrams)
        self.total_bigrams = float(sum(self.counts_of_bigram.values()))
        self.prob_of_bigram = {bg: self.counts_of_bigram[bg] / self.total_bigrams for bg in self.counts_of_bigram.keys()}
        
        # Build trigram model
        print("Building trigram model...")
        self.trigrams = list(nltk.trigrams(all_words))
        self.counts_of_trigram = Counter(self.trigrams)
        self.total_trigrams = float(sum(self.counts_of_trigram.values()))
        self.prob_of_trigram = {tg: self.counts_of_trigram[tg] / self.total_trigrams for tg in self.counts_of_trigram.keys()}
        
        print(f"Built models with {len(self.bigrams)} bigrams and {len(self.trigrams)} trigrams")

    def load_custom_words(self):
        """Load custom words from file if it exists."""
        try:
            if os.path.exists('custom_words.json'):
                with open('custom_words.json', 'r') as f:
                    data = json.load(f)
                    self.custom_words = set(data.get('words', []))
                    self.user_feedback = data.get('feedback', {})
                print(f"Loaded {len(self.custom_words)} custom words")
        except Exception as e:
            print(f"Could not load custom words: {e}")

    def save_custom_words(self):
        """Save custom words and user feedback to file."""
        try:
            data = {
                'words': list(self.custom_words),
                'feedback': self.user_feedback
            }
            with open('custom_words.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save custom words: {e}")

    def add_custom_word(self, word):
        """Add a custom word to the vocabulary."""
        word = word.lower()
        self.custom_words.add(word)
        self.vocabulary.add(word)
        self.prob_of_word[word] = 0.001
        self.save_custom_words()
        print(f"Added custom word: {word}")

    def record_user_feedback(self, original_word, suggested_word, accepted):
        """Record user feedback for learning."""
        if original_word not in self.user_feedback:
            self.user_feedback[original_word] = {}
        
        if suggested_word not in self.user_feedback[original_word]:
            self.user_feedback[original_word][suggested_word] = {'accepted': 0, 'rejected': 0}
        
        if accepted:
            self.user_feedback[original_word][suggested_word]['accepted'] += 1
        else:
            self.user_feedback[original_word][suggested_word]['rejected'] += 1
        
        self.save_custom_words()

    def edit1(self, word):
        """Generate all possible 1-edit distance variations."""
        letter = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        insert = [l + c + r for l, r in splits for c in letter]
        delete = [l + r[1:] for l, r in splits if r]
        replace = [l + c + r[1:] for l, r in splits if r for c in letter]
        swap = [l + r[1] + r[0] + r[2:] for l, r in splits if len(r) > 1]
        return set(replace + insert + delete + swap)

    def edit2(self, word):
        """Generate all possible 2-edit distance variations."""
        return [e2 for e1 in self.edit1(word) for e2 in self.edit1(e1)]

    def common_prefix_length(self, word1, word2):
        """Calculate the length of the common prefix between two words."""
        common_len = 0
        for i, (c1, c2) in enumerate(zip(word1, word2)):
            if c1 == c2:
                common_len += 1
            else:
                break
        return common_len

    def custom_score(self, suggestion, original_word):
        """Calculate custom score based on edit distance and operation type."""
        replace_weight = 1
        insert_weight = 2
        delete_weight = 3
        swap_weight = 4

        distance = editdistance.eval(suggestion, original_word)

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
        """Calculate combined score using edit distance and word probability."""
        edit_score = self.custom_score(suggestion, original_word)
        prob_score = -np.log(self.prob_of_word.get(suggestion, 1e-9))
        return edit_score + prob_score

    def should_use_context(self, word, previous_words):
        """Determine if we should use context-aware correction."""
        # Use context for common homophones and context-dependent words
        context_words = {
            'there', 'their', "they're",
            'your', "you're",
            'its', "it's",
            'to', 'too', 'two',
            'where', 'wear', 'were',
            'here', 'hear',
            'right', 'write',
            'know', 'no',
            'new', 'knew'
        }
        
        return word.lower() in context_words and len(previous_words) >= 1

    def context_aware_score(self, suggestion, original_word, previous_words):
        """Calculate context-aware score using n-grams."""
        # Base score
        base_score = self.combined_score(suggestion, original_word)
        
        # Context score using bigrams and trigrams
        context_score = 0
        
        if len(previous_words) >= 1:
            bigram_prob = self.prob_of_bigram.get((previous_words[-1], suggestion), 1e-9)
            context_score += -np.log(bigram_prob) * 2
        
        if len(previous_words) >= 2:
            trigram_prob = self.prob_of_trigram.get((previous_words[-2], previous_words[-1], suggestion), 1e-9)
            context_score += -np.log(trigram_prob) * 3
        
        # User feedback score
        feedback_score = 0
        if original_word in self.user_feedback and suggestion in self.user_feedback[original_word]:
            feedback = self.user_feedback[original_word][suggestion]
            total = feedback['accepted'] + feedback['rejected']
            if total > 0:
                acceptance_rate = feedback['accepted'] / total
                feedback_score = -np.log(1 - acceptance_rate) * 1.5
        
        # Custom word bonus
        custom_bonus = 0
        if suggestion in self.custom_words:
            custom_bonus = -3
        
        return base_score + context_score + feedback_score + custom_bonus

    def correct_spelling_hybrid(self, previous_words, word):
        """
        Hybrid spelling correction that intelligently chooses between approaches.
        """
        if word in self.vocabulary:
            return [(word, self.prob_of_word[word], 1.0)]

        suggestions = self.edit1(word).union(self.edit2(word))
        best_guesses = [w for w in suggestions if w in self.vocabulary]
        
        if not best_guesses:
            return [(word, 0, 0)]

        # Choose approach based on word type and context
        if self.should_use_context(word, previous_words):
            # Use context-aware approach for homophones
            best_guesses.sort(key=lambda w: self.context_aware_score(w, word, previous_words))
        else:
            # Use traditional approach for regular misspellings
            best_guesses.sort(key=lambda w: self.combined_score(w, word))
        
        return [(w, self.prob_of_word[w], self.get_context_probability(w, previous_words)) for w in best_guesses[:5]]

    def get_context_probability(self, word, previous_words):
        """Get the context probability for a word given previous words."""
        if len(previous_words) >= 2:
            trigram_prob = self.prob_of_trigram.get((previous_words[-2], previous_words[-1], word), 0)
            if trigram_prob > 0:
                return trigram_prob
        
        if len(previous_words) >= 1:
            return self.prob_of_bigram.get((previous_words[-1], word), 0)
        
        return 0

    def get_corpus_stats(self):
        """Get statistics about the corpus."""
        return {
            'total_words': len(self.vocabulary),
            'total_bigrams': len(self.bigrams),
            'total_trigrams': len(self.trigrams),
            'custom_words': len(self.custom_words),
            'user_feedback_entries': len(self.user_feedback)
        } 