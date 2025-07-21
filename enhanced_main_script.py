import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from autocorrect_package.enhanced_autocorrection import EnhancedAutocorrection
from autocorrect_package.autocorrection import Autocorrection
import language_tool_python
import re
import time

class EnhancedAutoCorrectApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enhanced AI Auto-Correction System")
        self.geometry("800x600")

        # Initialize the enhanced autocorrection system
        print("Initializing Enhanced Auto-Correction System...")
        self.enhanced_checker = EnhancedAutocorrection(use_large_corpora=True)
        
        # Initialize the original autocorrection system for medium mode
        print("Initializing Original Auto-Correction System...")
        self.original_checker = Autocorrection("autocorrect_package/corpus2.txt")
        
        # Set default checker
        self.checker = self.enhanced_checker

        # Initialize the grammar checker
        self.grammar_tool = language_tool_python.LanguageTool('en-US')

        # Create main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create top control panel
        self.create_control_panel()

        # Create text area and suggestions
        self.create_text_area()

        # Create bottom panel for custom words and stats
        self.create_bottom_panel()

        # Initialize variables
        self.current_word = ""
        self.previous_words = []
        self.grammar_popup = None
        self.correction_history = []
        self.synonym_popup = None
        self.last_synonym_tag = None
        self.last_synonym_badge_index = None

        # Bind events
        self.bind_events()

        # Show initial stats
        self.update_stats()

    def create_control_panel(self):
        """Create the top control panel with buttons and options."""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=5)
        control_frame.pack(fill="x", pady=(0, 10))

        # Left side - Mode selection
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(side="left", fill="x", expand=True)

        ttk.Label(mode_frame, text="Correction Mode:").pack(side="left")
        self.mode_var = tk.StringVar(value="enhanced")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                                 values=["enhanced", "medium", "basic"], state="readonly", width=10)
        mode_combo.pack(side="left", padx=(5, 10))

        # Right side - Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side="right")

        ttk.Button(button_frame, text="Add Custom Word", 
                  command=self.show_add_custom_word_dialog).pack(side="left", padx=2)
        ttk.Button(button_frame, text="View Custom Words", 
                  command=self.show_custom_words_dialog).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Add Shortcut", 
                  command=self.show_add_shortcut_dialog).pack(side="left", padx=2)
        ttk.Button(button_frame, text="View Shortcuts", 
                  command=self.show_shortcuts_dialog).pack(side="left", padx=2)
        ttk.Button(button_frame, text="Performance Stats", 
                  command=self.show_performance_stats).pack(side="left", padx=2)

    def create_text_area(self):
        """Create the main text area and suggestions panel."""
        text_frame = ttk.Frame(self.main_frame)
        text_frame.pack(fill="both", expand=True)

        # Left side - Text input
        left_frame = ttk.Frame(text_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(left_frame, text="Type your text here:").pack(anchor="w")
        
        # Text widget with scrollbar
        text_container = ttk.Frame(left_frame)
        text_container.pack(fill="both", expand=True)
        
        self.input_box = tk.Text(text_container, wrap="word", height=15)
        self.input_box.pack(side="left", fill="both", expand=True)
        
        text_scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=self.input_box.yview)
        text_scrollbar.pack(side="right", fill="y")
        self.input_box.configure(yscrollcommand=text_scrollbar.set)

        # Configure grammar error highlighting
        self.input_box.tag_configure("grammar_error", background="#ffcccc")

        # Right side - Suggestions
        right_frame = ttk.Frame(text_frame)
        right_frame.pack(side="right", fill="y", padx=(10, 0))

        ttk.Label(right_frame, text="Auto-Correction Suggestions:").pack(anchor="w")
        
        # Suggestion listbox with scrollbar
        suggestion_container = ttk.Frame(right_frame)
        suggestion_container.pack(fill="both", expand=True)
        
        self.suggestion_listbox = tk.Listbox(suggestion_container, width=30, height=10)
        self.suggestion_listbox.pack(side="left", fill="both", expand=True)
        
        suggestion_scrollbar = ttk.Scrollbar(suggestion_container, orient="vertical", 
                                           command=self.suggestion_listbox.yview)
        suggestion_scrollbar.pack(side="right", fill="y")
        self.suggestion_listbox.configure(yscrollcommand=suggestion_scrollbar.set)

        # Remove synonym label from the UI
        # self.synonym_label = ttk.Label(right_frame, text="", foreground="blue", wraplength=250, justify="left")
        # self.synonym_label.pack(fill="x", pady=(5, 0))

        # Grammar feedback label
        self.grammar_label = ttk.Label(right_frame, text="", foreground="red", 
                                      wraplength=250, justify="left")
        self.grammar_label.pack(fill="x", pady=(10, 0))

    def create_bottom_panel(self):
        """Create the bottom panel for statistics and information."""
        bottom_frame = ttk.LabelFrame(self.main_frame, text="System Information", padding=5)
        bottom_frame.pack(fill="x", pady=(10, 0))

        # Stats labels
        self.stats_frame = ttk.Frame(bottom_frame)
        self.stats_frame.pack(fill="x")

        self.total_words_label = ttk.Label(self.stats_frame, text="Total Words: Loading...")
        self.total_words_label.pack(side="left", padx=(0, 20))

        self.custom_words_label = ttk.Label(self.stats_frame, text="Custom Words: 0")
        self.custom_words_label.pack(side="left", padx=(0, 20))

        self.shortcuts_label = ttk.Label(self.stats_frame, text="Shortcuts: 0")
        self.shortcuts_label.pack(side="left", padx=(0, 20))

        self.corrections_label = ttk.Label(self.stats_frame, text="Corrections Made: 0")
        self.corrections_label.pack(side="left", padx=(0, 20))

        self.mode_label = ttk.Label(self.stats_frame, text="Mode: Enhanced")
        self.mode_label.pack(side="right")

    def bind_events(self):
        """Bind all keyboard and mouse events."""
        self.input_box.bind("<KeyRelease>", self.on_key_release)
        self.input_box.bind("<space>", self.on_space_bar_press)
        self.input_box.bind(".", self.on_sentence_end)
        self.input_box.bind("!", self.on_sentence_end)
        self.input_box.bind("?", self.on_sentence_end)
        self.suggestion_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

    def on_key_release(self, event):
        """Handle key release events for real-time suggestions."""
        cursor_position = self.input_box.index(tk.INSERT)
        current_line = self.input_box.get("insert linestart", cursor_position).split()
        
        self.current_word = current_line[-1] if current_line else ""
        self.previous_words = current_line[:-1] if len(current_line) > 1 else []
        
        self.autocorrect_suggestions()

    def on_space_bar_press(self, event):
        """Handle space bar press for auto-correction."""
        if self.suggestion_listbox.curselection():
            return

        word = self.current_word
        if not word:
            return

        # Separate punctuation
        match = re.match(r"([\w']+)([.,;!?:]*)", word)
        if match:
            word_part = match.group(1).lower()
            punct_part = match.group(2)
        else:
            word_part = word.lower()
            punct_part = ""

        # Get corrections based on mode
        mode = self.mode_var.get()
        if mode == "enhanced":
            corrections = self.enhanced_checker.correct_spelling_enhanced(self.previous_words, word_part)
        elif mode == "medium":
            corrections = self.original_checker.correct_spelling_with_context(self.previous_words[-1] if self.previous_words else "", word_part)
        else:  # basic mode
            corrections = self.original_checker.correct_spelling(word_part)

        if corrections and corrections[0][0] != word_part:
            correct_word = corrections[0][0]
            self.input_box.delete(f"insert-{len(word)}c", "insert")
            self.input_box.insert("insert", correct_word + punct_part + " ")
            
            # Record correction
            self.record_correction(word_part, correct_word)
            print(f"Auto-corrected '{word_part}' to '{correct_word}'")

        self.current_word = ""
        self.grammar_check_last_sentence()
        # Insert synonym badge after the last word
        self.insert_synonym_badge()

    def autocorrect_suggestions(self):
        """Show auto-correction suggestions."""
        word = self.current_word.lower()
        if len(word) < 3:
            self.suggestion_listbox.delete(0, tk.END)
            if hasattr(self, 'synonym_label'):
                self.synonym_label.config(text="")
            return

        # Get suggestions based on mode
        mode = self.mode_var.get()
        if mode == "enhanced":
            corrections = self.enhanced_checker.correct_spelling_enhanced(self.previous_words, word)
        elif mode == "medium":
            corrections = self.original_checker.correct_spelling_with_context(self.previous_words[-1] if self.previous_words else "", word)
        else:  # basic mode
            corrections = self.original_checker.correct_spelling(word)

        self.suggestion_listbox.delete(0, tk.END)
        synonyms_text = ""
        if corrections:
            for i, correction in enumerate(corrections[:5]):
                # For enhanced mode, correction may have synonyms as the 5th element
                if mode == "enhanced" and len(correction) >= 5:
                    word_suggestion = correction[0]
                    synonyms = correction[4]
                    if i == 0 and synonyms:
                        synonyms_text = f"Synonyms: {', '.join(synonyms)}"
                    self.suggestion_listbox.insert(tk.END, word_suggestion)
                else:
                    self.suggestion_listbox.insert(tk.END, correction[0])
        # Update the synonym label
        if hasattr(self, 'synonym_label'):
            self.synonym_label.config(text=synonyms_text)

    def on_listbox_select(self, event):
        """Handle suggestion selection."""
        if not self.suggestion_listbox.curselection():
            return

        selected_word = self.suggestion_listbox.get(self.suggestion_listbox.curselection())
        self.input_box.delete(f"insert-{len(self.current_word)}c", "insert")
        self.input_box.insert("insert", selected_word + " ")
        
        # Record user selection
        self.record_correction(self.current_word, selected_word)
        
        self.suggestion_listbox.delete(0, tk.END)
        self.current_word = ""

    def on_sentence_end(self, event):
        """Handle sentence ending punctuation."""
        self.grammar_check_last_sentence()

    def grammar_check_last_sentence(self):
        """Check grammar for the last sentence."""
        full_text = self.input_box.get("1.0", tk.END)
        sentences = re.split(r'([.!?])', full_text.strip())
        
        if len(sentences) >= 3:
            last_sentence = sentences[-3] + sentences[-2]
            start_idx = full_text.rfind(last_sentence)
        else:
            last_sentence = sentences[0]
            start_idx = full_text.rfind(last_sentence)

        matches = self.grammar_tool.check(last_sentence)
        self.input_box.tag_remove("grammar_error", "1.0", tk.END)

        if matches:
            suggestions = []
            for match in matches:
                suggestions.append(f"{match.context}\n→ {match.message}")
                error_start = start_idx + match.offset
                error_end = error_start + match.errorLength
                start_index = f"1.0+{error_start}c"
                end_index = f"1.0+{error_end}c"
                self.input_box.tag_add("grammar_error", start_index, end_index)
            
            self.grammar_label.config(text="\n".join(suggestions))
            self.show_grammar_popup(matches, start_idx)
        else:
            self.grammar_label.config(text="")

    def show_grammar_popup(self, matches, start_idx):
        """Show grammar suggestions popup."""
        if self.grammar_popup is None:
            self.grammar_popup = tk.Toplevel(self)
            self.grammar_popup.title("Grammar Suggestions")
            self.grammar_popup.geometry("400x300+{}+{}".format(
                self.winfo_x() + self.winfo_width() + 10, self.winfo_y()))
            
            self.input_box.focus_set()
            
            self.suggestions_frame = ttk.Frame(self.grammar_popup)
            self.suggestions_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            close_btn = ttk.Button(self.grammar_popup, text="Close", 
                                 command=self.close_grammar_popup)
            close_btn.pack(pady=5)
            
            self.after(100, self.input_box.focus_set)

        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self.suggestions_frame, text="Grammar Suggestions:", 
                               font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 10))

        for match in matches:
            suggestion = match.replacements[0] if match.replacements else None
            if suggestion:
                btn = ttk.Button(
                    self.suggestions_frame,
                    text=f"Replace '{match.context[match.offset:match.offset+match.errorLength]}' with '{suggestion}'\n→ {match.message}",
                    command=lambda m=match, s=suggestion: self.apply_grammar_correction(m, s, start_idx)
                )
                btn.pack(fill="x", pady=2)
            else:
                lbl = ttk.Label(self.suggestions_frame, 
                              text=f"{match.context}\n→ {match.message}", 
                              foreground="gray")
                lbl.pack(fill="x", pady=2)

    def close_grammar_popup(self):
        """Close the grammar popup."""
        if self.grammar_popup:
            self.grammar_popup.destroy()
            self.grammar_popup = None

    def apply_grammar_correction(self, match, suggestion, start_idx):
        """Apply a grammar correction."""
        error_start = start_idx + match.offset
        error_end = error_start + match.errorLength
        start_index = f"1.0+{error_start}c"
        end_index = f"1.0+{error_end}c"
        
        self.input_box.delete(start_index, end_index)
        self.input_box.insert(start_index, suggestion)
        self.input_box.tag_remove("grammar_error", "1.0", tk.END)
        self.update_grammar_popup()

    def update_grammar_popup(self):
        """Update the grammar popup with remaining suggestions."""
        full_text = self.input_box.get("1.0", tk.END)
        matches = self.grammar_tool.check(full_text)
        if matches:
            self.show_grammar_popup(matches, 0)
        else:
            self.close_grammar_popup()

    def show_add_custom_word_dialog(self):
        """Show dialog to add custom words."""
        if self.mode_var.get() != "enhanced":
            messagebox.showwarning("Feature Unavailable", 
                                 "Custom words are only available in Enhanced mode.\nPlease switch to Enhanced mode to use this feature.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Add Custom Word")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Enter a custom word:").pack(pady=10)
        
        word_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=word_var, width=30)
        entry.pack(pady=5)
        entry.focus()

        def add_word():
            word = word_var.get().strip().lower()
            if word:
                self.enhanced_checker.add_custom_word(word)
                self.update_stats()
                dialog.destroy()
                messagebox.showinfo("Success", f"Added custom word: {word}")

        ttk.Button(dialog, text="Add Word", command=add_word).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

    def show_custom_words_dialog(self):
        """Show dialog to view and manage custom words."""
        if self.mode_var.get() != "enhanced":
            messagebox.showwarning("Feature Unavailable", 
                                 "Custom words are only available in Enhanced mode.\nPlease switch to Enhanced mode to use this feature.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Custom Words")
        dialog.geometry("400x300")
        dialog.transient(self)

        ttk.Label(dialog, text="Your Custom Words:").pack(pady=10)

        # Create listbox with scrollbar
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        custom_words_list = tk.Listbox(list_frame)
        custom_words_list.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=custom_words_list.yview)
        scrollbar.pack(side="right", fill="y")
        custom_words_list.configure(yscrollcommand=scrollbar.set)

        # Populate list
        for word in sorted(self.enhanced_checker.custom_words):
            custom_words_list.insert(tk.END, word)

        def delete_word():
            selection = custom_words_list.curselection()
            if selection:
                word = custom_words_list.get(selection[0])
                self.enhanced_checker.custom_words.discard(word)
                self.enhanced_checker.vocabulary.discard(word)
                if word in self.enhanced_checker.prob_of_word:
                    del self.enhanced_checker.prob_of_word[word]
                self.enhanced_checker.save_custom_words()
                custom_words_list.delete(selection[0])
                self.update_stats()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Delete Selected", command=delete_word).pack(side="left")
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side="right")

    def show_add_shortcut_dialog(self):
        """Show dialog to add shortcuts."""
        if self.mode_var.get() != "enhanced":
            messagebox.showwarning("Feature Unavailable", 
                                 "Shortcuts are only available in Enhanced mode.\nPlease switch to Enhanced mode to use this feature.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Add Shortcut")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Add a shortcut mapping:").pack(pady=10)
        
        # Shortcut entry
        shortcut_frame = ttk.Frame(dialog)
        shortcut_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(shortcut_frame, text="Shortcut:").pack(side="left")
        shortcut_var = tk.StringVar()
        shortcut_entry = ttk.Entry(shortcut_frame, textvariable=shortcut_var, width=15)
        shortcut_entry.pack(side="left", padx=(5, 0))
        
        # Full word entry
        word_frame = ttk.Frame(dialog)
        word_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(word_frame, text="Full Word:").pack(side="left")
        word_var = tk.StringVar()
        word_entry = ttk.Entry(word_frame, textvariable=word_var, width=20)
        word_entry.pack(side="left", padx=(5, 0))
        
        shortcut_entry.focus()

        def add_shortcut():
            shortcut = shortcut_var.get().strip().lower()
            full_word = word_var.get().strip().lower()
            if shortcut and full_word:
                self.enhanced_checker.add_shortcut(shortcut, full_word)
                self.update_stats()
                dialog.destroy()
                messagebox.showinfo("Success", f"Added shortcut: '{shortcut}' → '{full_word}'")
            else:
                messagebox.showwarning("Error", "Please enter both shortcut and full word.")

        ttk.Button(dialog, text="Add Shortcut", command=add_shortcut).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

    def show_shortcuts_dialog(self):
        """Show dialog to view and manage shortcuts."""
        if self.mode_var.get() != "enhanced":
            messagebox.showwarning("Feature Unavailable", 
                                 "Shortcuts are only available in Enhanced mode.\nPlease switch to Enhanced mode to use this feature.")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Shortcuts")
        dialog.geometry("400x300")
        dialog.transient(self)

        ttk.Label(dialog, text="Your Shortcuts:").pack(pady=10)

        # Create listbox with scrollbar
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        shortcuts_list = tk.Listbox(list_frame)
        shortcuts_list.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=shortcuts_list.yview)
        scrollbar.pack(side="right", fill="y")
        shortcuts_list.configure(yscrollcommand=scrollbar.set)

        def delete_shortcut():
            selection = shortcuts_list.curselection()
            if selection:
                shortcut_text = shortcuts_list.get(selection[0])
                shortcut = shortcut_text.split(" → ")[0]
                if self.enhanced_checker.remove_shortcut(shortcut):
                    shortcuts_list.delete(selection[0])
                    self.update_stats()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Delete Selected", command=delete_shortcut).pack(side="left")
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side="right")

        # Load shortcuts
        shortcuts = self.enhanced_checker.get_all_shortcuts()
        for shortcut, full_word in sorted(shortcuts.items()):
            shortcuts_list.insert(tk.END, f"{shortcut} → {full_word}")

    def show_performance_stats(self):
        """Show detailed performance statistics."""
        mode = self.mode_var.get()
        
        if mode == "enhanced":
            stats = self.enhanced_checker.get_corpus_stats()
        else:
            # For medium and basic modes, use original system stats
            stats = {
                'total_words': len(self.original_checker.vocabulary),
                'total_bigrams': len(self.original_checker.bigrams),
                'total_trigrams': 0,
                'custom_words': 0,
                'user_feedback_entries': 0
            }
        
        dialog = tk.Toplevel(self)
        dialog.title("Performance Statistics")
        dialog.geometry("400x300")
        dialog.transient(self)

        ttk.Label(dialog, text=f"System Statistics - {mode.title()} Mode", font=("Arial", 14, "bold")).pack(pady=10)

        stats_text = f"""
Mode: {mode.title()}
Vocabulary Size: {stats['total_words']:,} words
Bigram Pairs: {stats['total_bigrams']:,}
Trigram Triplets: {stats['total_trigrams']:,}
Custom Words: {stats['custom_words']}
User Feedback Entries: {stats['user_feedback_entries']}
Corrections Made: {len(self.correction_history)}

Features Available:
- Enhanced: Large corpora, trigrams, custom words, user learning
- Medium: Original system with context-aware corrections
- Basic: Simple edit distance + word frequency
        """

        text_widget = tk.Text(dialog, height=15, width=45)
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)
        text_widget.insert("1.0", stats_text)
        text_widget.config(state="disabled")

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def record_correction(self, original_word, corrected_word):
        """Record a correction for learning."""
        self.correction_history.append({
            'original': original_word,
            'corrected': corrected_word,
            'timestamp': time.time()
        })
        
        # Only record feedback in enhanced mode
        if self.mode_var.get() == "enhanced":
            self.enhanced_checker.record_user_feedback(original_word, corrected_word, True)
        
        self.update_stats()

    def update_stats(self):
        """Update the statistics display."""
        mode = self.mode_var.get()
        if mode == "enhanced":
            stats = self.enhanced_checker.get_corpus_stats()
        else:
            # For medium and basic modes, use original system stats
            stats = {
                'total_words': len(self.original_checker.vocabulary),
                'custom_words': 0,  # Original system doesn't have custom words
                'total_bigrams': len(self.original_checker.bigrams),
                'total_trigrams': 0  # Original system doesn't have trigrams
            }
        
        self.total_words_label.config(text=f"Total Words: {stats['total_words']:,}")
        self.custom_words_label.config(text=f"Custom Words: {stats['custom_words']}")
        self.shortcuts_label.config(text=f"Shortcuts: {stats.get('shortcuts', 0)}")
        self.corrections_label.config(text=f"Corrections Made: {len(self.correction_history)}")
        self.mode_label.config(text=f"Mode: {mode.title()}")

    def run(self):
        """Start the application."""
        self.mainloop()

    def insert_synonym_badge(self):
        # Remove all previous synonym tags and popups
        self.input_box.tag_remove("synonym_badge", "1.0", tk.END)
        if hasattr(self, 'synonym_popup') and self.synonym_popup:
            self.synonym_popup.destroy()
            self.synonym_popup = None
        self.last_synonym_badge_index = None

        # Get all words in the text
        text = self.input_box.get("1.0", tk.END).rstrip("\n")
        if not text:
            print("No text in input_box.")
            return
        words = text.split()
        if not words:
            print("No words found.")
            return

        # Tag every word with synonyms
        idx = "1.0"
        chars_seen = 0
        line_start = int(self.input_box.index('end-1c').split('.')[0])
        text_no_trail = text.rstrip()
        for word in words:
            if len(word) < 3:
                chars_seen += len(word) + 1  # +1 for space or punctuation
                continue
            mode = self.mode_var.get()
            synonyms = []
            if mode == "enhanced":
                synonyms = self.enhanced_checker.get_synonyms(word)
            if not synonyms:
                chars_seen += len(word) + 1
                continue
            # Find the line and column of the word
            word_start_idx = None
            chars_counted = 0
            for line_num in range(1, line_start+1):
                line_text = self.input_box.get(f"{line_num}.0", f"{line_num}.end")
                if chars_counted + len(line_text) >= chars_seen:
                    col = chars_seen - chars_counted
                    word_start_idx = f"{line_num}.{col}"
                    break
                chars_counted += len(line_text) + 1  # +1 for newline
            if not word_start_idx:
                chars_seen += len(word) + 1
                continue
            word_end_idx = f"{word_start_idx}+{len(word)}c"
            tag_name = "synonym_badge"
            self.input_box.tag_add(tag_name, word_start_idx, word_end_idx)
            self.input_box.tag_configure(tag_name, foreground="blue", underline=True)
            self.input_box.tag_bind(tag_name, "<Enter>", lambda e, w=word, s=synonyms: self.show_synonym_popup(e, w, s))
            self.input_box.tag_bind(tag_name, "<Leave>", lambda e: self.hide_synonym_popup())
            self.input_box.tag_bind(tag_name, "<Button-1>", lambda e, w=word, s=synonyms: self.show_synonym_popup(e, w, s))
            print(f"Tagged word '{word}' at {word_start_idx}")
            chars_seen += len(word) + 1  # +1 for space or punctuation
        # Restore the cursor to the end
        self.input_box.mark_set(tk.INSERT, tk.END)

    def show_synonym_popup(self, event, word, synonyms):
        if hasattr(self, 'synonym_popup') and self.synonym_popup:
            self.synonym_popup.destroy()
        if not synonyms:
            return
        x = self.input_box.winfo_rootx() + event.x
        y = self.input_box.winfo_rooty() + event.y + 20
        self.synonym_popup = tk.Toplevel(self)
        self.synonym_popup.wm_overrideredirect(True)
        self.synonym_popup.geometry(f"+{x}+{y}")
        label = tk.Label(self.synonym_popup, text=f"Synonyms for '{word}':\n" + ", ".join(synonyms), background="lightyellow", borderwidth=1, relief="solid", justify="left")
        label.pack(ipadx=5, ipady=3)

    def hide_synonym_popup(self):
        if hasattr(self, 'synonym_popup') and self.synonym_popup:
            self.synonym_popup.destroy()
            self.synonym_popup = None

if __name__ == "__main__":
    app = EnhancedAutoCorrectApp()
    app.run() 