import pronouncing as pnc
import os
import markovify
import config
import string
import syllabifyARPA as arpa
import re

VOWELS = ['AA', 'AH', 'AW', 'EH', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']

class Poem:
    def __init__(self, pattern='AABB'):
        self.config = config.Config()

        all_text = ""
        for file in os.listdir(self.config.markovify_input_dir):
            with open(self.config.markovify_input_dir + file) as f:
                all_text += f.read()
        self.text_model = markovify.Text(all_text)

        self.poem = self.generate_poem(pattern)

    def generate_poem(self, pattern):
        line_pairings = {'A': None, 'B': None}

        for pair in line_pairings:
            print('Making line pair ' + pair + '. Looking for rhymes.')

            first = self._new_sentence()
            second = self._new_sentence()
            rhyme_attempts = 0
            max_attempts = 10000
            n = 0
            while (not is_rhyme_pair(first, second) and
                   rhyme_attempts < max_attempts):
                if rhyme_attempts % 50 == 0:
                    n += 1
                    print('\r' + n * '.', end='')
                if n == 20:
                    n = 0

                rhyme_attempts += 1

                if rhyme_attempts % 50 == 0:
                    first = self._new_sentence()

                second = self._new_sentence()

            line_pairs[pair] = '\n'.join([first, second])

            print()

        poem = '\n'.join(line_pairs.values())

        return poem

    def print_poem(self):

        print('*' * 40)
        print(self.poem)
        print('*' * 40)

    def _new_sentence(self):

        sent = self.text_model.make_short_sentence(
            (self.config.poem_first_syl_count
             * self.config.poem_avg_char_per_syl),
            max_overlap_ratio=self.config.markovify_max_overlap_ratio,
            max_overlap_total=self.config.markovify_max_overlap_total
        )
        if sent == None:
            return None
        else:
            return ''.join(c for c in sent if c not in string.punctuation)


class AaBbPoem:
    def __init__(self):
        self.config = config.Config()

        all_text = ""
        for file in os.listdir(self.config.markovify_input_dir):
            with open(self.config.markovify_input_dir + file) as f:
                all_text += f.read()
        self.text_model = markovify.Text(all_text)

        self.poem = self.generate_poem()

    def generate_poem(self):
        line_pairs = {'A': None, 'B': None}

        for pair in line_pairs:
            print('Making line pair ' + pair + '. Looking for rhymes.')

            first = self._new_sentence()
            second = self._new_sentence()
            rhyme_attempts = 0
            max_attempts = 10000
            n = 0
            while (not is_rhyme_pair(first, second) and
                   rhyme_attempts < max_attempts):
                if rhyme_attempts % 50 == 0:
                    n += 1
                    print('\r' + n * '.', end='')
                if n == 20:
                    n = 0

                rhyme_attempts += 1

                if rhyme_attempts % 50 == 0:
                    first = self._new_sentence()

                second = self._new_sentence()

            line_pairs[pair] = '\n'.join([first, second])

            print()

        poem = '\n'.join(line_pairs.values())

        return poem

    def print_poem(self):

        print('*' * 40)
        print(self.poem)
        print('*' * 40)

    def _new_sentence(self):

        sent = self.text_model.make_short_sentence(
            (self.config.poem_first_syl_count
             * self.config.poem_avg_char_per_syl),
            max_overlap_ratio=self.config.markovify_max_overlap_ratio,
            max_overlap_total=self.config.markovify_max_overlap_total
        )
        if sent == None:
            return None
        else:
            return ''.join(c for c in sent if c not in string.punctuation)


def rhyme_degree(target_word, test_word):
    """Returns a number between 0 and 1 as the degree of rhyming between two
    words, with 1 being an exact rhyme."""

    if test_word in pnc.rhymes(target_word):
        print('\rFound rhyme pair from the pronouncing library.')
        print(target_word, 'and', test_word)
        return 1

    # extract word part from last stressed syllable excluding that syll's onset
    rhymes = {target_word: None, test_word: None}
    for word in rhymes:
        try:
            pron = pnc.phones_for_word(word)[0]
        except IndexError:  # in case one of the words is not in the dictionary
            return 0
        # get stress pattern and find last stressed syllables
        stress = pnc.stresses(pron)
        last_stress = max([stress.rfind('1'), stress.rfind('2')])
        try:
            sylls = arpa.syllabifyARPA(pron, return_list=True)
        except ValueError:  # in case the word cannot be syllabified
            return 0
        sylls = sylls[last_stress:]
        first_onset = re.split(arpa.VOWELS_REGEX, sylls[0])[0]
        sylls[0] = sylls[0].replace(first_onset, '', 1)
        rhymes[word] = sylls

    # test for matching vowels and consonant clusters in onset and coda
    # the stressed vowel weighs double
    phones = 1 + max([sum(len(syll.split()) for syll in rhyme)
                      for rhyme in rhymes.values()])
    matches = 0
    for target_syll, test_syll in zip(rhymes[target_word], rhymes[test_word]):
        target_vowel = [phone for phone in target_syll.split()
                        if re.match(arpa.VOWELS_REGEX, phone)][0]
        test_vowel = [phone for phone in test_syll.split()
                      if re.match(arpa.VOWELS_REGEX, phone)][0]
        target_clusters = target_syll.split(target_vowel)
        test_clusters = test_syll.split(test_vowel)
        # measure match of syllable onsets
        matches += len(
            set(
                target_clusters[0].strip().split()
            ).intersection(
                set(test_clusters[0].strip().split())
            )
        )
        # measure match of vowels
        if target_vowel[:2] == test_vowel[:2]:  # test for the vowel itself
            matches += 1
            if (target_vowel[-1] in ['1', '2'] and
                target_vowel[-1] == test_vowel[-1]):  # test for similar stress
                matches +=1
        # measure match of syllable codas
        matches += len(
            set(
                target_clusters[1].strip().split()
            ).intersection(
                set(test_clusters[1].strip().split())
            )
        )
    degree = matches / phones
    if degree > 0.7:
        print('\rFound rhyme pair with a rhyming degree of: ', degree)
        print(rhymes)
    return degree


def is_rhyme_pair(target_line, test_line, same_allowed=False, min_degree=0.9):
    # TODO: rhyme proportion as keyword argument?
    """Return true if the passed lines rhyme."""

    if not target_line or target_line == '' or not test_line or test_line == '':
        return False

    target_last = target_line.split()[-1]
    test_last = test_line.split()[-1]

    if target_last.lower() == test_last.lower() and not same_allowed:
        return False

    # TODO: take into account short words
    degree = rhyme_degree(target_last, test_last)
    if degree > min_degree:
        return True
    else:
        return False


poem = AaBbPoem()
poem.print_poem()
