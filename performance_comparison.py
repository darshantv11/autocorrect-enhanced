#!/usr/bin/env python3
"""
Performance Comparison Script
Compares the original vs enhanced auto-correction systems
"""

import time
import json
from autocorrect_package.autocorrection import Autocorrection
from autocorrect_package.enhanced_autocorrection import EnhancedAutocorrection

def load_test_cases():
    """Load test cases for comparison."""
    test_cases = [
        # Basic spelling corrections
        ("thier", "their", ["forgot thier book", "thier house"]),
        ("recieve", "receive", ["I will recieve the package", "recieve payment"]),
        ("seperate", "separate", ["keep them seperate", "seperate rooms"]),
        ("occured", "occurred", ["it occured yesterday", "occured naturally"]),
        ("definately", "definitely", ["definately true", "definately going"]),
        
        # Context-dependent corrections
        ("there", "their", ["there book", "there house"]),
        ("there", "they're", ["there going", "there coming"]),
        ("your", "you're", ["your welcome", "your going"]),
        ("its", "it's", ["its time", "its here"]),
        ("to", "too", ["to much", "to many"]),
        
        # Technical terms (should be preserved)
        ("python", "python", ["python programming", "python code"]),
        ("api", "api", ["api endpoint", "api call"]),
        ("json", "json", ["json data", "json format"]),
        
        # Common misspellings
        ("beleive", "believe", ["I beleive you", "beleive in yourself"]),
        ("neccessary", "necessary", ["neccessary steps", "neccessary changes"]),
        ("accomodate", "accommodate", ["accomodate guests", "accomodate changes"]),
    ]
    return test_cases

def test_system(system, test_cases, system_name):
    """Test a system with given test cases."""
    print(f"\n{'='*50}")
    print(f"Testing {system_name}")
    print(f"{'='*50}")
    
    results = {
        'correct_corrections': 0,
        'incorrect_corrections': 0,
        'no_suggestions': 0,
        'total_time': 0,
        'vocabulary_size': len(system.vocabulary),
        'test_cases': []
    }
    
    for original, expected, contexts in test_cases:
        print(f"\nTesting: '{original}' → Expected: '{expected}'")
        
        for context in contexts:
            start_time = time.time()
            
            # Extract previous word for context
            words = context.split()
            if original in words:
                word_index = words.index(original)
                previous_words = words[:word_index]
                current_word = original
            else:
                previous_words = words[:-1] if len(words) > 1 else []
                current_word = words[-1] if words else original
            
            # Get corrections
            if hasattr(system, 'correct_spelling_enhanced'):
                corrections = system.correct_spelling_enhanced(previous_words, current_word)
            else:
                corrections = system.correct_spelling(current_word)
            
            end_time = time.time()
            results['total_time'] += (end_time - start_time)
            
            # Analyze results
            if corrections:
                top_suggestion = corrections[0][0]
                if top_suggestion == expected:
                    results['correct_corrections'] += 1
                    print(f"  ✓ Correct: '{original}' → '{top_suggestion}'")
                else:
                    results['incorrect_corrections'] += 1
                    print(f"  ✗ Wrong: '{original}' → '{top_suggestion}' (expected: '{expected}')")
            else:
                results['no_suggestions'] += 1
                print(f"  ? No suggestions for '{original}'")
            
            # Store detailed results
            results['test_cases'].append({
                'original': original,
                'expected': expected,
                'context': context,
                'suggestions': [c[0] for c in corrections] if corrections else [],
                'time': end_time - start_time
            })
    
    return results

def print_comparison(original_results, enhanced_results):
    """Print comparison between the two systems."""
    print(f"\n{'='*60}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*60}")
    
    # Calculate accuracy
    original_total = original_results['correct_corrections'] + original_results['incorrect_corrections']
    enhanced_total = enhanced_results['correct_corrections'] + enhanced_results['incorrect_corrections']
    
    original_accuracy = (original_results['correct_corrections'] / original_total * 100) if original_total > 0 else 0
    enhanced_accuracy = (enhanced_results['correct_corrections'] / enhanced_total * 100) if enhanced_total > 0 else 0
    
    print(f"{'Metric':<25} {'Original':<15} {'Enhanced':<15} {'Improvement':<15}")
    print("-" * 70)
    print(f"{'Vocabulary Size':<25} {original_results['vocabulary_size']:<15,} {enhanced_results['vocabulary_size']:<15,} {enhanced_results['vocabulary_size'] - original_results['vocabulary_size']:<15,}")
    print(f"{'Correct Corrections':<25} {original_results['correct_corrections']:<15} {enhanced_results['correct_corrections']:<15} {enhanced_results['correct_corrections'] - original_results['correct_corrections']:<15}")
    print(f"{'Incorrect Corrections':<25} {original_results['incorrect_corrections']:<15} {enhanced_results['incorrect_corrections']:<15} {original_results['incorrect_corrections'] - enhanced_results['incorrect_corrections']:<15}")
    print(f"{'No Suggestions':<25} {original_results['no_suggestions']:<15} {enhanced_results['no_suggestions']:<15} {original_results['no_suggestions'] - enhanced_results['no_suggestions']:<15}")
    print(f"{'Accuracy (%)':<25} {original_accuracy:<15.1f} {enhanced_accuracy:<15.1f} {enhanced_accuracy - original_accuracy:<15.1f}")
    print(f"{'Total Time (s)':<25} {original_results['total_time']:<15.3f} {enhanced_results['total_time']:<15.3f} {enhanced_results['total_time'] - original_results['total_time']:<15.3f}")
    
    # Calculate improvement percentage
    if original_accuracy > 0:
        improvement_pct = ((enhanced_accuracy - original_accuracy) / original_accuracy) * 100
        print(f"\nOverall Improvement: {improvement_pct:.1f}%")
    
    # Save detailed results
    comparison_data = {
        'original_system': original_results,
        'enhanced_system': enhanced_results,
        'comparison': {
            'original_accuracy': original_accuracy,
            'enhanced_accuracy': enhanced_accuracy,
            'improvement_percentage': improvement_pct if original_accuracy > 0 else 0,
            'vocabulary_improvement': enhanced_results['vocabulary_size'] - original_results['vocabulary_size']
        }
    }
    
    with open('performance_comparison_results.json', 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    print(f"\nDetailed results saved to 'performance_comparison_results.json'")

def main():
    """Main function to run the performance comparison."""
    print("AI Auto-Correction System Performance Comparison")
    print("=" * 60)
    
    # Load test cases
    test_cases = load_test_cases()
    print(f"Loaded {len(test_cases)} test cases")
    
    # Initialize systems
    print("\nInitializing systems...")
    
    print("Loading original system...")
    original_system = Autocorrection("autocorrect_package/corpus2.txt")
    
    print("Loading enhanced system...")
    enhanced_system = EnhancedAutocorrection(use_large_corpora=True)
    
    # Run tests
    original_results = test_system(original_system, test_cases, "Original System")
    enhanced_results = test_system(enhanced_system, test_cases, "Enhanced System")
    
    # Print comparison
    print_comparison(original_results, enhanced_results)
    
    print(f"\n{'='*60}")
    print("COMPARISON COMPLETE")
    print(f"{'='*60}")
    print("The enhanced system should show significant improvements in:")
    print("• Vocabulary size (more words available)")
    print("• Accuracy (better context understanding)")
    print("• Coverage (fewer 'no suggestions' cases)")
    print("\nCheck 'performance_comparison_results.json' for detailed analysis.")

if __name__ == "__main__":
    main() 