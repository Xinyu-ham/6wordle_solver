import tkinter as tk
from tkinter import font
from tkinter import messagebox
from game import Game

class Board():
    def __init__(self, game):
        self.root = tk.Tk()
        self.root.geometry("430x510")
        self.root.title("XY's 6-letter Wordle")
        self.root.wm_iconbitmap('hamlet.ico')
        self.game = game
        self.labels = []
        self.entry = None
        self.solver = None

    def set_header(self):
        header_font = font.Font(size=15, family='Helvetica')
        # txt = f'Word: {self.game.answer}'
        print(self.game.answer)
        txt = 'Welcome to XY\'s Wordle rip-off'
        header = tk.Label(
            self.root,
            text=txt,
        )
        header.grid(row=0, column=0, columnspan=6)
        header['font'] = header_font

    def create_input(self):
        e = tk.Entry(self.root, width=20)
        e.grid(row=1, column=0, columnspan=2)

        guess_button = tk.Button(self.root, text='Guess', command=self.update_row)
        guess_button.grid(row=1, column=2, columnspan=2)
        self.root.bind('<Return>', lambda event: self.update_row())
        self.entry = e

        solve_button = tk.Button(self.root, text='Auto-solve', command=self.auto_solve)
        solve_button.grid(row=1, column=4, columnspan=2)


    def generate_labels(self):
        label_font = font.Font(size=20, family='Helvetica')
        labels = []
        for i in range(6):
            row = []
            for j in range(6):
                label = tk.Label(
                    self.root,
                    text=f'?',
                    bg='gray',
                    borderwidth=3,
                    relief='groove',
                    width='4',
                    height='2'
                )
                row.append(label)
                label.grid(row=i + 3, column=j)
                label['font'] = label_font
            labels.append(row)
        self.labels = labels

    def create_help_row(self):
        help_font = font.Font(size=10, family='Helvetica')

        help = tk.Label(
            self.root,
            text=f'Wrong letters: None',
            fg='gray'
        )
        help.grid(row=2, column=0, columnspan=6)
        help['font'] = help_font

        self.help = help

    def update_help_row(self):
        used_letters = self.game.used_letters
        self.help.config(text=f"Wrong letters: {', '.join(used_letters)}")

    def update_row(self):
        tries = self.game.guesses
        word = self.entry.get().lower()
        if not word.isalpha():
            messagebox.showinfo('Invalid characters', f'"{word}" contains non-alphabets.')
            return
        if len(word) != 6:
            messagebox.showinfo('Invalid length', f'"{word}" has {len(word)} letters, not 6.')
            return
        if not self.game.check_valid(word):
            messagebox.showinfo('Invalid word', f'"{word}" is not a word we know.')
            return

        self.display_guess(word, tries)

    def display_guess(self, word, tries):
        states = self.game.make_guess(word)
        labels = self.labels[tries]

        for i, label in enumerate(labels):
            self.set_label(label, word[i], states[i])

        self.update_help_row()

        if all([s==3 for s in states]):
            messagebox.showinfo('Congratulations',f'You guessed the word: {self.game.answer} in {self.game.guesses} tries.')
            self.game.status = 'win'
            return

        if self.game.guesses == 6:
            messagebox.showinfo('You moron',
                                f'The answer is obviously {self.game.answer}.')
            self.game.status = 'lose'
        return states

    def start(self):
        self.set_header()
        self.create_input()
        self.generate_labels()
        self.create_help_row()
        self.root.mainloop()

    def set_label(self, label, letter, state):
        cmap = ['', '#555555', '#FDFD96', '#C1E1C1']
        label.config(
            relief='sunken',
            bg=cmap[state],
            text=letter
        )

    def auto_solve(self):
        from autosolver import WordleSolver
        self.solver = WordleSolver(self.game)

        if self.game.guesses > 0:
            print('Adding constraints')
            for guess in range(self.game.guesses):
                word = self.game.history[guess]
                states = self.game.grid[guess]
                self._update_solver(word, states)
        else:
            self.display_guess('eunoia', 0)

        while self.game.status == 'active':
            self._solve()


    def _solve(self):
        guess = self.solver.solve(dropout=0.8)
        print(guess)
        states = self.display_guess(guess, self.game.guesses)
        if self.game.status != 'active':
            return
        self._update_solver(guess, states)

    def _update_solver(self, word, states):
        def word_breakdown(word, states):
            breakdown = {}
            for i in range(self.game.word_length):
                letter = word[i]
                state = states[i]
                if letter not in breakdown:
                    breakdown[letter] = []
                breakdown[letter].append((i, state))
            return breakdown

        breakdown = word_breakdown(word, states)

        for letter in breakdown:
            if len(breakdown[letter]) == 1:
                column = breakdown[letter][0][0]
                state = breakdown[letter][0][1]
                if state == 1:  # Wrong letter
                    self.solver.add_exclusion_constraint(letter)
                elif state == 2:  # Correct letter wrong position
                    self.solver.add_inclusion_constraint(letter, 1, False)
                    self.solver.add_not_position_constraint(letter, column)
                else:  # Correct letter and position
                    self.solver.add_exact_constraint(letter, column)
            else:
                counter = 0
                exact = False
                occurances = len(breakdown[letter])
                for i in range(occurances):
                    column = breakdown[letter][i][0]
                    state = breakdown[letter][i][1]
                    if state == 1:  # Wrong letter
                        exact = True
                    elif state == 2:  # Correct letter wrong position
                        self.solver.add_not_position_constraint(letter, column)
                        counter += 1
                    else:  # Correct letter and position
                        self.solver.add_exact_constraint(letter, column)
                        counter += 1
                self.solver.add_inclusion_constraint(letter, counter, exact)
        print(len(self.solver.dictionary))




if __name__ == '__main__':
    test = Game()
    board = Board(test)
    board.start()
