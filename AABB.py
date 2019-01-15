import pronouncing as pnc
import os
import markovify
import config
import string as str


class AABB_poem:
    def __init__(self, ):
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
            print('Making line pair ' + pair)

            first = self._new_sentence()
            second = self._new_sentence()
            rhyme_attempts = 0
            max_attempts = 10000
            while (not is_rhyme_pair(first, second) and
                   rhyme_attempts < max_attempts):
                n = rhyme_attempts % 25
                print('\r' + n * '.' + (10 - n) * ' ', end='')
                rhyme_attempts += 1

                if rhyme_attempts % 100 == 0:
                    first = self._new_sentence()

                second = self._new_sentence()

            line_pairs[pair] = '\n'.join([first, second])

            print()

        poem = '\n'.join(line_pairs.values())

        return poem

    def print_poem(self):

        print('*' * 50)
        print(self.poem)
        print('*' * 50)

    def _new_sentence(self):

        sent = self.text_model.make_short_sentence(
            (self.config.poem_first_syl_count
             * self.config.poem_avg_char_per_syl),
            tries=100,
            max_overlap_ratio=self.config.markovify_max_overlap_ratio,
            max_overlap_total=self.config.markovify_max_overlap_total
        )
        if not sent:
            return None
        else:
            return ''.join(c for c in sent if c not in str.punctuation)


def rhyme_degree(target_word, test_word):
    """Returns a number between 0 and 1 as the degree of rhyming between two
    words, with 1 being an exact rhyme."""

    if test_word in pnc.rhymes(target_word):
        return 1

    # test phone for phone how well the words match
    try:
        target_pron = pnc.phones_for_word(target_word)[0].split()
        test_pron = pnc.phones_for_word(test_word)[0].split()
    except IndexError:  # in case one of the words is not in the dictionary
        return 0
    phone_count = 0
    matches = 0
    # TODO: take into account consonant clusters and the weight of stressed syllables
    # TODO: use syllabifyARPA
    reverse_target = reversed(target_pron)
    reverse_test = reversed(test_pron)
    for target, test in zip(reverse_target, reverse_test):
        if target == test:
            matches +=1
        phone_count += 1
    if phone_count == 0:
        return 0
    else:
        return matches/phone_count


def is_rhyme_pair(target_line, test_line, same_allowed=False, min_degree=0.7):
    # TODO: rhyme proportion as keyword argument?
    """Return true if the passed lines rhyme."""

    if not target_line or target_line == '' or not test_line or test_line == '':
        return False

    target_last = target_line.split()[-1]
    test_last = test_line.split()[-1]

    if target_last.lower() == test_last.lower() and not same_allowed:
        return False

    # TODO: take into account short words

    if rhyme_degree(target_last, test_last) > min_degree:
        return True
    else:
        return False


poem = AABB_poem()
poem.print_poem()