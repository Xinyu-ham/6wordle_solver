from random import randrange

# Load a list of 6-letter words
with open('dictionary.txt') as f:
    dictionary = f.read()
dictionary = dictionary.split(', ')


class Game():
    def __init__(self, word=None):
        self.word_length = 6
        self.dictionary = dictionary
        if word:
            self.answer = word
        else:
            self.answer = dictionary[randrange(len(dictionary))]
        self.guesses = 0
        self.history = []  # Pass guesses
        self.grid = []  # Board color for each guess
        self.used_letters = [] # Letters appearing in previous guesses not in word
        self.status = 'active'


    def check_valid(self, word):
        return word in self.dictionary

    def make_guess(self, word):
        def get_state(answer, letter, position):
            if answer[position] == letter:
                return 3
            elif letter in answer:
                return 2
            else:
                return 1

        answer = self.answer
        states = []


        for i, letter in enumerate(word):
            states.append(get_state(answer, word[i], i))
            if letter not in self.used_letters and letter not in answer:
                self.used_letters.append(letter)

        dup = {}
        for i, letter in enumerate(word):
            if list(word).count(letter) > list(answer).count(letter):
                if letter not in dup:
                    dup[letter] = (
                        list(answer).count(letter),
                        [],
                        []
                    )
                dup[letter][1].append(i)

        for letter in dup:
            while len(dup[letter][1]) > dup[letter][0]:
                i = dup[letter][1].pop()
                if states[i] == 3:
                    dup[letter][1].insert(0, i)
                else:
                    states[i] = 1

        self.grid.append(states)
        self.history = word
        self.guesses += 1
        return states