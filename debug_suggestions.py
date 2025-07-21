#!/usr/bin/env python3
"""
Debug script to show how auto-correction suggestions are generated
"""

import string
import re
from collections import Counter
import editdistance
import numpy as np
import nltk
from nltk.corpus import brown, reuters
import json
import os

def edit1(word):
    """Generate all possible 1-edit distance variations."""
    letter = string.ascii_lowercase
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    insert = [l + c + r for l, r in splits for c in letter]
    delete = [l + r[1:] for l, r in splits if r]
    replace = [l + c + r[1:] for l, r in splits if r for c in letter]
    swap = [l + r[1] + r[0] + r[2:] for l, r in splits if len(r) > 1]
    return set(replace + insert + delete + swap)

def edit2(word):
    """Generate all possible 2-edit distance variations."""
    return [e2 for e1 in edit1(word) for e2 in edit1(e1)]

def debug_suggestions(word, mode="enhanced"):
    """Debug how suggestions are generated for a word."""
    
    print(f"🔍 DEBUGGING SUGGESTIONS FOR: '{word}'")
    print(f"📋 MODE: {mode.upper()}")
    print("=" * 60)
    
    # Step 1: Generate edit distance variations
    print("1️⃣ GENERATING EDIT DISTANCE VARIATIONS:")
    edit1_variations = edit1(word)
    edit2_variations = edit2(word)
    all_variations = edit1_variations.union(set(edit2_variations))
    
    print(f"   Edit-1 variations: {len(edit1_variations)}")
    print(f"   Edit-2 variations: {len(edit2_variations)}")
    print(f"   Total variations: {len(all_variations)}")
    
    # Show some examples
    edit1_examples = list(edit1_variations)[:10]
    print(f"   Edit-1 examples: {edit1_examples}")
    
    # Step 2: Load vocabulary based on mode
    print(f"\n2️⃣ LOADING VOCABULARY ({mode.upper()} MODE):")
    
    if mode == "enhanced":
        # Load enhanced vocabulary
        try:
            # Load custom words
            custom_words = set()
            if os.path.exists('custom_words.json'):
                with open('custom_words.json', 'r') as f:
                    data = json.load(f)
                    custom_words = set(data.get('words', []))
            
            # Load original corpus
            with open("autocorrect_package/corpus2.txt", "r", encoding="utf-8") as file:
                original_words = []
                lines = file.readlines()
                for line in lines:
                    original_words += re.findall(r'\w+', line.lower())
            
            # Load large corpora
            brown_words = [word.lower() for word in brown.words() if word.isalpha()]
            reuters_words = [word.lower() for word in reuters.words() if word.isalpha()]
            
            # Combine all vocabularies
            all_words = original_words + brown_words + reuters_words + list(custom_words)
            vocabulary = set(all_words)
            
            print(f"   Original corpus words: {len(set(original_words))}")
            print(f"   Brown corpus words: {len(set(brown_words))}")
            print(f"   Reuters corpus words: {len(set(reuters_words))}")
            print(f"   Custom words: {len(custom_words)}")
            print(f"   Total vocabulary: {len(vocabulary)}")
            
        except Exception as e:
            print(f"   Error loading enhanced vocabulary: {e}")
            return
            
    else:
        # Load basic vocabulary
        try:
            with open("autocorrect_package/corpus2.txt", "r", encoding="utf-8") as file:
                words = []
                lines = file.readlines()
                for line in lines:
                    words += re.findall(r'\w+', line.lower())
            vocabulary = set(words)
            print(f"   Basic vocabulary: {len(vocabulary)} words")
        except Exception as e:
            print(f"   Error loading basic vocabulary: {e}")
            return
    
    # Step 3: Filter variations by vocabulary
    print(f"\n3️⃣ FILTERING BY VOCABULARY:")
    valid_suggestions = [w for w in all_variations if w in vocabulary]
    print(f"   Valid suggestions found: {len(valid_suggestions)}")
    
    if valid_suggestions:
        print(f"   Top suggestions: {valid_suggestions[:10]}")
    else:
        print(f"   No valid suggestions found!")
    
    # Step 4: Check if original word is in vocabulary
    print(f"\n4️⃣ CHECKING ORIGINAL WORD:")
    if word in vocabulary:
        print(f"   ✅ '{word}' is in vocabulary - no correction needed!")
    else:
        print(f"   ❌ '{word}' is NOT in vocabulary - needs correction")
    
    # Step 5: Show ranking (if we have suggestions)
    if valid_suggestions:
        print(f"\n5️⃣ SUGGESTION RANKING:")
        
        # Simple ranking by edit distance
        ranked_suggestions = []
        for suggestion in valid_suggestions:
            distance = editdistance.eval(word, suggestion)
            ranked_suggestions.append((suggestion, distance))
        
        # Sort by edit distance
        ranked_suggestions.sort(key=lambda x: x[1])
        
        print(f"   Top 10 suggestions by edit distance:")
        for i, (suggestion, distance) in enumerate(ranked_suggestions[:10]):
            print(f"   {i+1}. '{suggestion}' (distance: {distance})")
    
    print("\n" + "=" * 60)

def main():
    """Main function to debug suggestions."""
    
    # Test words
    test_words = ["rahul", "surya", "rakesh", "python", "api", "json"]
    
    print("🔧 AUTO-CORRECTION SUGGESTION DEBUGGER")
    print("=" * 60)
    
    for word in test_words:
        print(f"\n{'='*20} TESTING '{word.upper()}' {'='*20}")
        
        # Test in basic mode
        debug_suggestions(word, "basic")
        
        # Test in enhanced mode
        debug_suggestions(word, "enhanced")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    main() 