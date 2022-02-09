from itertools import permutations
import numpy as np

class WordleSolver():
    def __init__(self, game):
        self.game_word_length = game.word_length
        self.dictionary = game.dictionary
        self.game = game

    def add_exact_constraint(self, letter, column):
        self.dictionary = [word for word in self.dictionary if word[column] == letter]

    def add_not_position_constraint(self, letter, column):
        self.dictionary = [word for word in self.dictionary if word[column] != letter]

    def add_inclusion_constraint(self, letter, occurances, exact):
        if occurances == 0:
            self.add_exclusion_constraint(letter)
        elif exact:
            self.dictionary = [word for word in self.dictionary if word.count(letter) == occurances]
        else:
            self.dictionary = [word for word in self.dictionary if word.count(letter) >= occurances]

    def add_exclusion_constraint(self, letter):
        self.dictionary = [word for word in self.dictionary if letter not in word]

    def solve(self, dropout=0):
        assert dropout < 1 and dropout >= 0
        sequences = list(permutations(range(self.game_word_length)))
        indices = [int(x) for x in np.linspace(0, len(sequences), round((1-dropout) * len(sequences)))]
        sequences = [seq for i, seq in enumerate(sequences) if i in indices]
        possible_guesses = []
        for sequence in sequences:
            possible_guesses.append(self._get_sequence_score(sequence))

        guess, score = tuple(sorted(possible_guesses, key=lambda x:x[1], reverse=True))[0]
        print(f'Guessing word: {guess} with probability of {score:.3f}')
        return guess

    def _get_sequence_score(self, sequence):
        word_list = self.dictionary
        letters = []
        for column in sequence:

            guess = self._get_column_common_letter(column, word_list)
            letters.append(guess)
            word_list = [word for word in word_list if word[column] == guess[0]]


        word = ['']*self.game_word_length
        score = 1
        for letter in letters:
            word[letter[2]] = letter[0]
            score *= letter[1]
        word = ''.join(word)
        print(sequence, word, score)
        return [word, score]


    def _get_column_common_letter(self, column, word_list):
        total_words = len(word_list)
        letters = [word[column] for word in word_list]

        letter_score_dict = {letter:(letters.count(letter) /total_words) for letter in letters}
        max_score = max(letter_score_dict.values())
        return [letter_score + (column,) for letter_score in letter_score_dict.items() if letter_score[1] == max_score][0]

    # def _get_best_letters_each_position(self):
    #     return ''.join(
    #         [self._get_column_common_letters(col) for col in range(self.game_word_length)]
    #     )
    #
    # def _find_closest_word(self, best_letters):
    #     def similarity(word1, word2):
    #         assert len(word1) == len(word2)
    #         word_len = len(word1)
    #         return sum(
    #             [1 if word1[i]==word2[i] else 0 for i in range(word_len)]
    #         )
    #
    #     word_similarity_scores = {word:similarity(best_letters, word) for word in self.dictionary}
    #     max_score = max(word_similarity_scores.values())
    #     for word in word_similarity_scores:
    #         if word_similarity_scores[word] == max_score:
    #             return word
    #
    # def solve(self):
    #     best_letters = self._get_best_letters_each_position()
    #     return self._find_closest_word(best_letters)