#!/usr/bin/env python3
"""
Test script for the shortcut functionality
Demonstrates how shortcuts work in the enhanced autocorrection system.
"""

from autocorrect_package.enhanced_autocorrection import EnhancedAutocorrection

def test_shortcuts():
    """Test the shortcut functionality."""
    
    print("Testing Shortcut Functionality")
    print("=" * 50)
    
    # Initialize the enhanced autocorrection system
    corrector = EnhancedAutocorrection()
    
    # Add some example shortcuts
    print("\nAdding example shortcuts...")
    corrector.add_shortcut("bcz", "because")
    corrector.add_shortcut("mrn", "morning")
    corrector.add_shortcut("evng", "evening")
    corrector.add_shortcut("tmrw", "tomorrow")
    corrector.add_shortcut("yr", "year")
    corrector.add_shortcut("msg", "message")
    corrector.add_shortcut("txt", "text")
    corrector.add_shortcut("pls", "please")
    corrector.add_shortcut("thx", "thanks")
    corrector.add_shortcut("btw", "by the way")
    
    # Test shortcut expansion
    test_shortcuts = [
        "bcz", "mrn", "evng", "tmrw", "yr", "msg", "txt", "pls", "thx", "btw"
    ]
    
    print("\nTesting shortcut expansion:")
    print("-" * 30)
    for shortcut in test_shortcuts:
        expansion = corrector.get_shortcut_expansion(shortcut)
        if expansion:
            print(f"'{shortcut}' → '{expansion}'")
        else:
            print(f"'{shortcut}' → No expansion found")
    
    # Test autocorrection with shortcuts
    print("\nTesting autocorrection with shortcuts:")
    print("-" * 40)
    
    test_sentences = [
        "I will see you tmrw",
        "Thx for the msg",
        "Pls send me the txt",
        "Btw, I will be late",
        "Good mrn everyone",
        "See you in the evng"
    ]
    
    for sentence in test_sentences:
        print(f"\nOriginal: {sentence}")
        words = sentence.lower().split()
        corrected_words = []
        
        for word in words:
            # Check if it's a shortcut
            expansion = corrector.get_shortcut_expansion(word)
            if expansion:
                corrected_words.append(expansion)
                print(f"  '{word}' → '{expansion}' (shortcut)")
            else:
                corrected_words.append(word)
        
        corrected_sentence = " ".join(corrected_words)
        print(f"Corrected: {corrected_sentence}")
    
    # Test with context
    print("\nTesting shortcuts with context:")
    print("-" * 35)
    
    context_words = ["good", "morning", "how", "are", "you"]
    test_word = "mrn"
    
    print(f"Context: {' '.join(context_words)}")
    print(f"Word: '{test_word}'")
    
    suggestions = corrector.correct_spelling_enhanced(context_words, test_word)
    print("Suggestions:")
    for i, suggestion_data in enumerate(suggestions[:3]):
        if len(suggestion_data) == 4:
            suggestion, prob, context_prob, info = suggestion_data
            print(f"  {i+1}. {suggestion} (prob: {prob:.6f}, context: {context_prob:.6f}) - {info}")
        else:
            suggestion, prob, context_prob = suggestion_data
            print(f"  {i+1}. {suggestion} (prob: {prob:.6f}, context: {context_prob:.6f})")
    
    # Show all shortcuts
    print(f"\nAll shortcuts ({len(corrector.shortcuts)}):")
    print("-" * 25)
    for shortcut, full_word in sorted(corrector.shortcuts.items()):
        print(f"'{shortcut}' → '{full_word}'")
    
    # Test removing a shortcut
    print(f"\nRemoving shortcut 'btw'...")
    if corrector.remove_shortcut("btw"):
        print("Successfully removed 'btw'")
    
    # Show updated shortcuts
    print(f"\nUpdated shortcuts ({len(corrector.shortcuts)}):")
    print("-" * 30)
    for shortcut, full_word in sorted(corrector.shortcuts.items()):
        print(f"'{shortcut}' → '{full_word}'")
    
    # Test system stats
    stats = corrector.get_corpus_stats()
    print(f"\nSystem Statistics:")
    print("-" * 20)
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    test_shortcuts() 