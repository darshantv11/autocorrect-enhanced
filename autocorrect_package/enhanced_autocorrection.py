import string
import re
from collections import Counter
import editdistance
import numpy as np
import nltk
from nltk.corpus import brown, reuters
import json
import os
# Add SymSpellPy import
from symspellpy.symspellpy import SymSpell, Verbosity

class EnhancedAutocorrection(object):
    """
    Enhanced autocorrection system using multiple large corpora and n-gram models.
    """

    def __init__(self, original_corpus_file="autocorrect_package/corpus2.txt", use_large_corpora=True):
        self.use_large_corpora = use_large_corpora
        self.custom_words = set()
        self.shortcuts = {}  # Dictionary to store shortcuts: {"bcz": "because", "mrn": "morning"}
        self.user_feedback = {}  # Track user corrections for learning
        # SymSpellPy initialization
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        dict_path = os.path.join(os.path.dirname(__file__), "frequency_dictionary_en_82_765.txt")
        if os.path.exists(dict_path):
            self.sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)
        else:
            print(f"Warning: SymSpell frequency dictionary not found at {dict_path}")
        # Load original corpus
        self.original_words = self.load_original_corpus(original_corpus_file)
        
        # Load large corpora if enabled
        if use_large_corpora:
            self.large_corpus_words = self.load_large_corpora()
            # Combine all words
            all_words = self.original_words + self.large_corpus_words
        else:
            all_words = self.original_words
        
        # Build vocabulary and statistics
        self.build_vocabulary(all_words)
        
        # Load custom words and shortcuts if they exist
        self.load_custom_words()
        self.load_shortcuts()
        
        print(f"Enhanced Autocorrection initialized with {len(self.vocabulary)} unique words and {len(self.shortcuts)} shortcuts")

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
            # Load Brown corpus (1M+ words from various domains)
            print("Loading Brown corpus...")
            brown_words = brown.words()
            words.extend([word.lower() for word in brown_words if word.isalpha()])
            print(f"Loaded {len(brown_words)} words from Brown corpus")
            
        except Exception as e:
            print(f"Warning: Could not load Brown corpus: {e}")
        
        try:
            # Load Reuters corpus (news articles)
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
        
        # Build bigram (2-gram) model
        print("Building bigram model...")
        self.bigrams = list(nltk.bigrams(all_words))
        self.counts_of_bigram = Counter(self.bigrams)
        self.total_bigrams = float(sum(self.counts_of_bigram.values()))
        self.prob_of_bigram = {bg: self.counts_of_bigram[bg] / self.total_bigrams for bg in self.counts_of_bigram.keys()}
        
        # Build trigram (3-gram) model for better context
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

    def load_shortcuts(self):
        """Load shortcuts from file if it exists."""
        try:
            if os.path.exists('shortcuts.json'):
                with open('shortcuts.json', 'r') as f:
                    self.shortcuts = json.load(f)
                print(f"Loaded {len(self.shortcuts)} shortcuts")
        except Exception as e:
            print(f"Could not load shortcuts: {e}")

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

    def save_shortcuts(self):
        """Save shortcuts to file."""
        try:
            with open('shortcuts.json', 'w') as f:
                json.dump(self.shortcuts, f, indent=2)
        except Exception as e:
            print(f"Could not save shortcuts: {e}")

    def add_custom_word(self, word):
        """Add a custom word to the vocabulary."""
        word = word.lower()
        self.custom_words.add(word)
        self.vocabulary.add(word)
        # Give custom words high probability
        self.prob_of_word[word] = 0.001  # Higher than average
        self.save_custom_words()
        print(f"Added custom word: {word}")

    def add_shortcut(self, shortcut, full_word):
        """Add a shortcut mapping."""
        shortcut = shortcut.lower()
        full_word = full_word.lower()
        
        # Add the shortcut mapping
        self.shortcuts[shortcut] = full_word
        
        # Also add the full word to custom words if it's not in vocabulary
        if full_word not in self.vocabulary:
            self.add_custom_word(full_word)
        
        self.save_shortcuts()
        print(f"Added shortcut: '{shortcut}' → '{full_word}'")

    def remove_shortcut(self, shortcut):
        """Remove a shortcut mapping."""
        shortcut = shortcut.lower()
        if shortcut in self.shortcuts:
            full_word = self.shortcuts.pop(shortcut)
            self.save_shortcuts()
            print(f"Removed shortcut: '{shortcut}' → '{full_word}'")
            return True
        return False

    def get_shortcut_expansion(self, word):
        """Get the full word for a shortcut if it exists."""
        return self.shortcuts.get(word.lower(), None)

    def is_shortcut(self, word):
        """Check if a word is a shortcut."""
        return word.lower() in self.shortcuts

    def get_all_shortcuts(self):
        """Get all shortcut mappings."""
        return self.shortcuts.copy()

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

    def enhanced_context_score(self, suggestion, original_word, previous_words):
        """Calculate enhanced context score using n-grams and user feedback."""
        # Base score (edit distance + word probability) - give this more weight
        base_score = self.combined_score(suggestion, original_word) * 2  # Double the weight
        
        # Context score using bigrams and trigrams - reduce weight
        context_score = 0
        
        if len(previous_words) >= 1:
            # Bigram score
            bigram_prob = self.prob_of_bigram.get((previous_words[-1], suggestion), 1e-9)
            context_score += -np.log(bigram_prob) * 0.5  # Reduce bigram weight
        
        if len(previous_words) >= 2:
            # Trigram score
            trigram_prob = self.prob_of_trigram.get((previous_words[-2], previous_words[-1], suggestion), 1e-9)
            context_score += -np.log(trigram_prob) * 1.0  # Reduce trigram weight
        
        # User feedback score
        feedback_score = 0
        if original_word in self.user_feedback and suggestion in self.user_feedback[original_word]:
            feedback = self.user_feedback[original_word][suggestion]
            total = feedback['accepted'] + feedback['rejected']
            if total > 0:
                acceptance_rate = feedback['accepted'] / total
                feedback_score = -np.log(1 - acceptance_rate) * 1.5  # Moderate user feedback weight
        
        # Custom word bonus
        custom_bonus = 0
        if suggestion in self.custom_words:
            custom_bonus = -3  # Moderate preference for custom words
        
        return base_score + context_score + feedback_score + custom_bonus

    def correct_spelling_enhanced(self, previous_words, word):
        """
        SymSpellPy-only spelling correction (ignores custom corpus for suggestions).
        """
        # First check if it's a shortcut
        shortcut_expansion = self.get_shortcut_expansion(word)
        if shortcut_expansion:
            return [(shortcut_expansion, 1.0, 1.0, "Shortcut expansion")]

        # If word is in SymSpell dictionary, return it as correct
        if word in self.sym_spell._words:
            return [(word, 1.0, 1.0, "SymSpellPy")]

        # Use SymSpellPy for fast spelling suggestions
        symspell_suggestions = self.sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2, include_unknown=True)
        if symspell_suggestions:
            results = []
            for suggestion in symspell_suggestions[:5]:
                sug_word = suggestion.term
                prob = suggestion.count  # Use SymSpell frequency count
                results.append((sug_word, prob, 1.0, "SymSpellPy"))
            return results

        # If no suggestions found, return the original word
        return [(word, 0, 0, "No suggestion")]

    def get_context_probability(self, word, previous_words):
        """Get the context probability for a word given previous words."""
        if len(previous_words) >= 2:
            # Try trigram first
            trigram_prob = self.prob_of_trigram.get((previous_words[-2], previous_words[-1], word), 0)
            if trigram_prob > 0:
                return trigram_prob
        
        if len(previous_words) >= 1:
            # Fall back to bigram
            return self.prob_of_bigram.get((previous_words[-1], word), 0)
        
        return 0

    def get_corpus_stats(self):
        """Get statistics about the corpus."""
        return {
            'total_words': len(self.vocabulary),
            'total_bigrams': len(self.bigrams),
            'total_trigrams': len(self.trigrams),
            'custom_words': len(self.custom_words),
            'shortcuts': len(self.shortcuts),
            'user_feedback_entries': len(self.user_feedback)
        } 

    def get_synonyms(self, word, max_synonyms=5):
        """Get synonyms for a word using WordNet."""
        from nltk.corpus import wordnet
        print(f"Looking up synonyms for: {word}")
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                name = lemma.name().replace('_', ' ').lower()
                if name != word.lower():
                    synonyms.add(name)
        result = list(synonyms)[:max_synonyms]
        print(f"Found synonyms for '{word}': {result}")
        return result 