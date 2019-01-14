import pronouncing as pnc
import os
import markovify
import config
import string as str


class AABB_poem:
    def __init__(self):
        self.config = config.Config()
        self.poem = self.generate_poem()

    def generate_poem(self):

        all_text = ""
        for file in os.listdir(self.config.markovify_input_dir):
            with open(self.config.markovify_input_dir + file) as f:
                all_text += f.read()
        text_model = markovify.Text(all_text)

        # TODO: consider a better way of attempting to find rhyming lines
        # maybe:
        line_pairs = {'A': None, 'B': None}

        for pair in line_pairs:
            print("Making line pair " + pair)

            print(".", end='')
            first = text_model.make_short_sentence(
                (self.config.poem_first_syl_count
                 * self.config.poem_avg_char_per_syl),
                tries=100,
                max_overlap_ratio=self.config.markovify_max_overlap_ratio,
                max_overlap_total=self.config.markovify_max_overlap_total
            )
            first = ''.join(c for c in first if c not in str.punctuation)

            text_model.make_sentence()
            second = None
            rhyme_attempts = 0
            max_attempts = 100
            while (not is_rhyme_pair(first, second) and
                   rhyme_attempts < max_attempts):
                print(".", end='')

                second = text_model.make_short_sentence(
                    (self.config.poem_second_syl_count
                     * self.config.poem_avg_char_per_syl),
                    tries=100,
                    max_overlap_ratio=self.config.markovify_max_overlap_ratio,
                    max_overlap_total=self.config.markovify_max_overlap_total
                )
                second = ''.join(c for c in second if c not in str.punctuation)

            line_pairs[pair] = '\n'.join([first, second])

        poem = '\n'.join(line_pairs.values())

        print("")
        print("***********************")
        print("-----------------------")
        print(poem)
        print("-----------------------")
        print("***********************")

        return poem


def rhyme_degree(target_word, test_word):
    """Returns a number between 0 and 1 as the degree of rhyming between two
    words, with 1 being an exact rhyme."""

    if test_word in pnc.rhymes(target_word):
        return 1

    # test with just the rhyming part
    try:
        target_pron = pnc.phones_for_word(target_word)
        target_rhyme = pnc.rhyming_part(target_pron[0])
    except IndexError:  # in case the word is not in the dictionary
        print('Warning: ', target_word, ' is not in the dictionary.')
        return 0
    if test_word in pnc.search(target_rhyme):
        return 1

    # test phone for phone how well the words match in their rhyming parts
    try:
        test_pron = pnc.phones_for_word(test_word)
        test_rhyme = pnc.rhyming_part(test_pron[0])
    except IndexError:  # in case the word is not in the dictionary
        print('Warning: ', test_word, ' is not in the dictionary.')
        return 0
    phone_count = 0
    matches = 0
    # TODO: take into account consonant clusters and the weight of stressed syllables
    for target, test in zip(reversed(target_rhyme), reversed(test_rhyme)):
        if target == test:
            matches +=1
        phone_count += 1
    if phone_count == 0:
        return 0
    else:
        return matches/phone_count


def is_rhyme_pair(target_line, test_line, minimum_sylls=3):
    # TODO: rhyme proportion as keyword argument?
    """Return true if the passed lines rhyme."""

    if not target_line or target_line == '' or not test_line or test_line == '':
        return False

    target_last = target_line.split()[-1]
    test_last = test_line.split()[-1]

    # TODO: take into account short words
    if rhyme_degree(target_last, test_last) > 0.8:
        return True
    else:
        return False


poem = AABB_poem()