import tkinter as tk
import numpy as np
from autocorrect_package.autocorrection import Autocorrection
import language_tool_python
import re

class AutoCorrectApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize the Autocorrection object with the desired file
        self.checker = Autocorrection("autocorrect_package/corpus2.txt")

        # Initialize the grammar checker
        self.grammar_tool = language_tool_python.LanguageTool('en-US')

        # Create an input box(Text widget) for the user to type
        self.input_box = tk.Text(self, wrap="word")
        self.input_box.pack()

        # Creating a Listbox widget to display suggestions
        self.suggestion_listbox = tk.Listbox(self)
        self.suggestion_listbox.pack()

        # Label to display grammar suggestions
        self.grammar_label = tk.Label(self, text="", fg="red", wraplength=500, justify="left")
        self.grammar_label.pack()

        # Configure tag for grammar errors
        self.input_box.tag_configure("grammar_error", background="#ffcccc")

        # Initialize grammar popup as None (will be created when needed)
        self.grammar_popup = None

        # Bind the key release event to call the on_key_release method
        self.input_box.bind("<KeyRelease>", self.on_key_release)

        # Bind the space bar event to call the on_space_bar_press method
        self.input_box.bind("<space>", self.on_space_bar_press)
        # Bind period, exclamation, and question mark to trigger grammar check
        self.input_box.bind(".", self.on_sentence_end)
        self.input_box.bind("!", self.on_sentence_end)
        self.input_box.bind("?", self.on_sentence_end)
        
        # Bind the listbox select event to call the on_listbox_select method
        self.suggestion_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        # Initialize a variable to store the current word being typed
        self.current_word = ""

    def on_key_release(self, event):
        # Get the current position of the cursor(insertion point)
        cursor_position = self.input_box.index(tk.INSERT)

        # Get the words currently being typed by the user
        current_line = self.input_box.get("insert linestart", cursor_position).split()
        self.current_word = current_line[-1] if current_line else ""
        self.previous_word = current_line[-2] if len(current_line) > 1 else ""

        # Show suggestions immediately as the user types
        self.autocorrect_suggestions()

    def on_space_bar_press(self, event):
        # Check if any suggestion was selected from the suggestion box
        if self.suggestion_listbox.curselection():
            return

        # If no suggestion is selected, proceed with autocorrection logic

        # Get the current and previous word being typed by the user
        word = self.current_word
        prev_word = self.previous_word.lower() if hasattr(self, 'previous_word') else ""

        # Separate trailing punctuation from the word
        match = re.match(r"([\w']+)([.,;!?:]*)", word)
        if match:
            word_part = match.group(1).lower()
            punct_part = match.group(2)
        else:
            word_part = word.lower()
            punct_part = ""

        # Perform the autocorrection logic using the Autocorrection class (context-aware)
        corrections = self.checker.correct_spelling_with_context(prev_word, word_part)
        if not corrections:
            return

        # Get the word with the highest probability from the corrections list
        if corrections:
            probs = np.array([c[1] for c in corrections])
            best_ix = np.argmax(probs)
            correct = corrections[0][0]
            highest_prob_word = correct
        
            # Replace the wrong word with the word with the highest probability, preserving punctuation
            if highest_prob_word != word_part or punct_part:
                self.input_box.delete(f"insert-{len(word)}c", "insert")
                self.input_box.insert("insert", highest_prob_word + punct_part + "")

            print(f"Did you mean {highest_prob_word}{punct_part}?")

        self.current_word = ""

        # --- Grammar checking logic ---
        # Get the full text and check the last sentence
        full_text = self.input_box.get("1.0", tk.END)
        sentences = full_text.strip().split('.')
        if len(sentences) > 1:
            last_sentence = sentences[-2] + '.'  # The sentence just completed
            # Calculate the start index of the last sentence
            start_idx = full_text.rfind(last_sentence)
        else:
            last_sentence = sentences[-1]
            start_idx = full_text.rfind(last_sentence)
        matches = self.grammar_tool.check(last_sentence)

        # Remove previous highlights
        self.input_box.tag_remove("grammar_error", "1.0", tk.END)

        if matches:
            suggestions = []
            for i, match in enumerate(matches):
                suggestions.append(f"{match.context}\n→ {match.message}")
                # Highlight the error in the Text widget
                error_start = start_idx + match.offset
                error_end = error_start + match.errorLength
                # Convert to Tkinter index
                start_index = f"1.0+{error_start}c"
                end_index = f"1.0+{error_end}c"
                self.input_box.tag_add("grammar_error", start_index, end_index)
            self.grammar_label.config(text="\n".join(suggestions))
            self.show_grammar_popup(matches, start_idx)
        else:
            self.grammar_label.config(text="")

    def autocorrect_suggestions(self):
        # Get the current and previous word being typed by the user
        word = self.current_word.lower()
        prev_word = self.previous_word.lower() if hasattr(self, 'previous_word') else ""
        if len(word) < 3:
            return

        # Perform the autocorrection logic using the Autocorrection class (context-aware)
        corrections = self.checker.correct_spelling_with_context(prev_word, word)

        # Clear the existing suggestions from the listbox
        self.suggestion_listbox.delete(0, tk.END)

        # Show the suggestions in the listbox
        if corrections:
            for correction in corrections:
                self.suggestion_listbox.insert(tk.END, correction[0])
    
    def on_listbox_select(self, event):
        # Get the selected word from the listbox
        selected_word = self.suggestion_listbox.get(self.suggestion_listbox.curselection())

        # Replace the current word in the input box with the selected word
        self.input_box.delete(f"insert-{len(self.current_word)}c", "insert")
        self.input_box.insert("insert", selected_word + " ")

        # Clear the existing suggestions from the listbox after selecting one
        self.suggestion_listbox.delete(0, tk.END)

    def on_sentence_end(self, event):
        # Trigger grammar checking logic after sentence-ending punctuation
        self.grammar_check_last_sentence()

    def grammar_check_last_sentence(self):
        full_text = self.input_box.get("1.0", tk.END)
        # Find the last sentence ending with ., !, or ?
        import re
        sentences = re.split(r'([.!?])', full_text.strip())
        if len(sentences) >= 3:
            last_sentence = sentences[-3] + sentences[-2]  # sentence + punctuation
            start_idx = full_text.rfind(last_sentence)
        else:
            last_sentence = sentences[0]
            start_idx = full_text.rfind(last_sentence)
        matches = self.grammar_tool.check(last_sentence)
        # Remove previous highlights
        self.input_box.tag_remove("grammar_error", "1.0", tk.END)
        if matches:
            suggestions = []
            for i, match in enumerate(matches):
                suggestions.append(f"{match.context}\n→ {match.message}")
                # Highlight the error in the Text widget
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
        # Create popup only if it doesn't exist
        if self.grammar_popup is None:
            self.grammar_popup = tk.Toplevel(self)
            self.grammar_popup.title("Grammar Suggestions")
            self.grammar_popup.geometry("400x300+{}+{}".format(self.winfo_x() + self.winfo_width() + 10, self.winfo_y()))
            # Do NOT block the main window; allow user to continue typing
            # No grab_set, no transient
            
            # Ensure the main text widget keeps focus
            self.input_box.focus_set()
            
            # Create a frame to hold all suggestions
            self.suggestions_frame = tk.Frame(self.grammar_popup)
            self.suggestions_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Add a close button
            close_btn = tk.Button(self.grammar_popup, text="Close", command=self.close_grammar_popup)
            close_btn.pack(pady=5)
            
            # Force focus back to text widget after popup creation
            self.after(100, self.input_box.focus_set)
        
        # Clear previous suggestions
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        # Add title
        title_label = tk.Label(self.suggestions_frame, text="Grammar Suggestions:", fg="blue", font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Add new suggestions
        for i, match in enumerate(matches):
            suggestion = match.replacements[0] if match.replacements else None
            if suggestion:
                btn = tk.Button(
                    self.suggestions_frame,
                    text=f"Replace '{match.context[match.offset:match.offset+match.errorLength]}' with '{suggestion}'\n→ {match.message}",
                    wraplength=380,
                    justify="left",
                    anchor="w",
                    command=lambda m=match, s=suggestion: self.apply_grammar_correction(m, s, start_idx)
                )
                btn.pack(fill="x", pady=2)
            else:
                lbl = tk.Label(self.suggestions_frame, text=f"{match.context}\n→ {match.message}", wraplength=380, justify="left", fg="gray")
                lbl.pack(fill="x", pady=2)

    def close_grammar_popup(self):
        if self.grammar_popup:
            self.grammar_popup.destroy()
            self.grammar_popup = None

    def apply_grammar_correction(self, match, suggestion, start_idx):
        # Calculate the error's absolute position in the text
        error_start = start_idx + match.offset
        error_end = error_start + match.errorLength
        start_index = f"1.0+{error_start}c"
        end_index = f"1.0+{error_end}c"
        # Replace the error with the suggestion
        self.input_box.delete(start_index, end_index)
        self.input_box.insert(start_index, suggestion)
        # Remove highlights
        self.input_box.tag_remove("grammar_error", "1.0", tk.END)
        # Update the popup with remaining suggestions or close if none
        self.update_grammar_popup()

    def update_grammar_popup(self):
        # Re-check for grammar errors and update popup
        full_text = self.input_box.get("1.0", tk.END)
        matches = self.grammar_tool.check(full_text)
        if matches:
            # Find the position of the first error for highlighting
            first_match = matches[0]
            start_idx = 0  # For full text check
            self.show_grammar_popup(matches, start_idx)
        else:
            # No more errors, close popup
            self.close_grammar_popup()

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = AutoCorrectApp()
    app.run()
