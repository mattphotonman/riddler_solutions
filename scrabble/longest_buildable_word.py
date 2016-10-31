"""
Code for finding the longest word you can build out
of valid words one letter at a time.

http://fivethirtyeight.com/features/this-challenge-will-boggle-your-mind/
"""
from collections import defaultdict

def load_words(filename):
    """
    Loads the words into separate sets for each
    word length.
    """
    words = defaultdict(set)
    for line in open(filename):
        word = line.strip()
        words[len(word)].add(word)
    return words

def find_buildable_words(all_words):
    """
    Input is a dictionary of sets of words of each
    length, where the key is the length. Output is
    the same structure but with the sets containing
    only 'buildable' words.  A buildable word is
    one that can be built one letter at a time from
    other words in the dictionary.
    """
    min_length = min(all_words.iterkeys())
    max_length = max(all_words.iterkeys())
    buildable_words = {min_length : all_words[min_length]}
    for word_length in range(min_length + 1, max_length + 1):
        buildable_words[word_length] = set()
        for word in all_words[word_length]:
            if word[:-1] in buildable_words[word_length - 1] or \
               word[1:] in buildable_words[word_length - 1]:
                buildable_words[word_length].add(word)
        if len(buildable_words[word_length]) == 0:
            del buildable_words[word_length]
            break
    return buildable_words

def get_build_sequence(word, buildable_words):
    """
    Using the output of find_buildable_words, return
    the sequence of words out of which the input
    word can be built.
    """
    output_seq = [[word]]
    min_length = min(buildable_words.iterkeys())
    for word_length in range(len(word) - 1, min_length - 1, -1):
        new_words = set()
        for prev_word in output_seq[-1]:
            if prev_word[:-1] in buildable_words[word_length]:
                new_words.add(prev_word[:-1])
            if prev_word[1:] in buildable_words[word_length]:
                new_words.add(prev_word[1:])
        output_seq.append(list(new_words))
    return output_seq

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dictionary_file')
    parser.add_argument('outfile')
    parser.add_argument('-b', '--buildseq', required = False,
                        action = 'store_true')

    args = vars(parser.parse_args())

    all_words = load_words(args['dictionary_file'])
    buildable_words = find_buildable_words(all_words)

    max_buildable_words = max(buildable_words.iteritems(),
                              key = lambda (word_length, _) : word_length)[1]
    if args['buildseq']:
        with open(args['outfile'], 'w') as fout:
            for word in max_buildable_words:
                for building_blocks in get_build_sequence(word,
                                                          buildable_words):
                    print >> fout, ' '.join(building_blocks)
                print >> fout
        print "Results written to", args['outfile']
    elif len(max_buildable_words) > 10:
        with open(args['outfile'], 'w') as fout:
            for word in max_buildable_words:
                print >> fout, word
        print "Results written to", args['outfile']
    else:
        for word in max_buildable_words:
            print word
