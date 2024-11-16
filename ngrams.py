import numpy as np

class NGram(object):

    def __init__(self, gram):
        '''
        Initializes the n-gram model with the type of n-gram model it is (unigram, bigram, trigram)
        '''
        pass

    def read_ngram(self, features):
        """
        Takes the feature vector, and extracts the unique words and their
        respective counts. Keys in the n-gram dictionary dependent on what
        type of model it is

        returns the number of unique tokens in the model for that n-gram
        Initializes the number of words and vocab size fields
        """
        pass

    def calc_loglikelihoods(self, sentence):
        """
        Calculates the sum of the log likelihoods of the sentence
        """
        pass

    def model_perplexity(self, sequence, smoothing=0):
        """
        Calculates the perplexity of the model given the data set
        and its prior mapping information

        Note: takes in a list of tokenized input
        """
        llp = 0
        M = 0
        for sentence in sequence:
            llp += self.calc_loglikelihoods(sentence, smoothing)
            M += len(sentence) - 1
        avg_llp = (- 1. / M) * llp
        return 2. ** avg_llp


class Unigram(NGram):
    def __init__ (self):
        self.perplexity = np.nan
        self.unigram = {"<START>": 0, "<STOP>" : 0, "<UNK>" : 0}
        self.num_words = 0
        self.vocab_size = None
        
    def read_ngram(self, features):
        """
        Reads the features and counts the occurrences of each word.
        Words with less than 3 occurrences are treated as unknown.
        """
        initial_unigram = {"<START>": 0, "<STOP>" : 0}
        for sentence in features:
            for word in sentence:
                if word in initial_unigram:
                    initial_unigram[word] += 1
                else:
                    initial_unigram[word] = 1

        for key, val in initial_unigram.items():
            if val < 3:
                self.unigram["<UNK>"] += val
            else:
                self.unigram[key] = val
        
        self.num_words = sum(self.unigram.values()) - self.unigram["<START>"]
        self.vocab_size = len(self.unigram) - 1
        return len(self.unigram) - 1    
    
    def probability(self, word, smoothing=0):
        """
        Calculates the probability of a word with optional smoothing.
        """
        if word in self.unigram:
            return (self.unigram[word] + smoothing) / (self.num_words + (smoothing * self.vocab_size))
        else:
            return (self.unigram["<UNK>"] + smoothing) / (self.num_words + (smoothing * self.vocab_size))

    def calc_loglikelihoods(self, sentence, smoothing=0):
        """
        Calculates the log likelihood of a sentence.
        """
        llp = 0
        for word in sentence[1:]:
            llp += np.log2(self.probability(word, smoothing))
        return llp

    def get_unigram(self):
        """
        Returns the unigram dictionary.
        """
        return self.unigram

    def get_vocab(self):
        """
        Returns the vocabulary size.
        """
        return self.vocab_size

class Bigram(NGram):
    def __init__ (self):
        self.perplexity = None
        self.bigram = {}
        self.unigram = Unigram()
        self.num_words = 0
        self.vocab_size = None

    def read_ngram(self, features):
        """
        Reads the features and counts the occurrences of each bigram.
        """
        for sentence in features:
            for i, word in enumerate(sentence[:-1]):
                bi = (word, sentence[i+1])
                if bi not in self.bigram:
                    self.bigram[bi] = 1
                else:
                    self.bigram[bi] +=1

        self.unigram.read_ngram(features)
        self.num_words = sum(self.bigram.values())
        self.vocab_size = self.unigram.get_vocab()
        return len(self.bigram)

    def probability(self, words, smoothing=0):
        """
        Calculates the probability of a bigram with optional smoothing.
        """
        if words[0] in self.unigram.get_unigram():
            return (self.bigram[words] + smoothing) / (self.unigram.get_unigram()[words[0]] + (smoothing * self.vocab_size))
        else:
            return (self.bigram[words] + smoothing) / (self.unigram.get_unigram()["<UNK>"] + (smoothing * self.vocab_size))

    def calc_loglikelihoods(self, sentence, smoothing=0):
        """
        Calculates the log likelihood of a sentence.
        """
        llp = 0
        unigram = self.unigram.get_unigram()
        for i, word in enumerate(sentence[:-1]):
            bi = (word, sentence[i+1])
            if bi not in self.bigram or word not in unigram or bi[1] not in unigram: continue
            llp += np.log2(self.probability(bi,smoothing))
        return llp

    def get_vocab(self):
        """
        Returns the vocabulary size.
        """
        return self.vocab_size
    
    def get_bigram(self):
        """
        Returns the bigram dictionary.
        """
        return self.bigram
    
    
class Trigram(NGram):
    def __init__ (self):
        self.perplexity = None
        self.trigram = {}
        self.bigram = Bigram()
        self.num_words = 0
        self.vocab_size = None
    
    def read_ngram(self, features):
        """
        Reads the features and counts the occurrences of each trigram.
        """
        for sentence in features:
            for i, word in enumerate(sentence[:-2]):
                tri = (word, sentence[i+1], sentence[i+2])
                if tri not in self.trigram:
                    self.trigram[tri] = 1
                else:
                    self.trigram[tri] += 1

        self.bigram.read_ngram(features)
        self.num_words = sum(self.trigram.values())
        self.vocab_size = self.bigram.get_vocab()
        return len(self.trigram)

    def probability(self, words, smoothing=0):
        """
        Calculates the probability of a trigram with optional smoothing.
        """
        return (self.trigram[words] + smoothing) / (self.bigram.get_bigram()[(words[0], words[1])] + (smoothing * self.vocab_size))

    def calc_loglikelihoods(self, sentence, smoothing=0):
        """
        Calculates the log likelihood of a sentence.
        """
        bigram = self.bigram.get_bigram()
        first = tuple(sentence[0:2])
        if first in bigram:
            llp = np.log2(self.bigram.probability(first, smoothing))
        else:
            llp = 0
        for i, word in enumerate(sentence[:-2]):
            tri = (word, sentence[i+1], sentence[i+2])
            if tri not in self.trigram or (word, sentence[i+1]) not in bigram: continue
            llp += np.log2(self.probability(tri,smoothing))
        return llp

    def get_trigram(self):
        """
        Returns the trigram dictionary.
        """
        return self.trigram
    
    def get_vocab(self):
        """
        Returns the vocabulary size.
        """
        return self.vocab_size

class InterpolatedNGram():

    def __init__ (self):
        self.unigram = Unigram()
        self.bigram = Bigram()
        self.trigram = Trigram()

    def train(self, features):
        """
        Trains the unigram, bigram, and trigram models with the given features.
        """
        self.unigram.read_ngram(features)
        self.bigram.read_ngram(features)
        self.trigram.read_ngram(features)

    def calc_loglikelihoods(self, sentence, lams):
        """
        Calculates the log likelihood of a sentence using interpolation.
        """
        l1, l2, l3 = lams
        bigram = self.bigram.get_bigram()
        unigram = self.unigram.get_unigram()
        trigram = self.trigram.get_trigram()
        first_two = tuple(sentence[0:2])

        if first_two in bigram:
            ptri = pbi = self.bigram.probability(first_two)
            if sentence[1] in unigram:
                pun = self.unigram.probability(sentence[1])
            else:
                pun = 0
            llp = np.log2(l1 * pun + l2 * pbi + l3 * ptri)
        else:
            llp = 0
        for i, word in enumerate(sentence[:-2]):
            tri = (word, sentence[i+1], sentence[i+2])
            bi = (sentence[i+1], sentence[i+2])
            un = sentence[i+2]
            if tri not in trigram or (word, sentence[i+1]) not in bigram or sentence[i+2] not in unigram: continue
            ptri = self.trigram.probability(tri)
            pbi = self.bigram.probability(bi)
            pun = self.unigram.probability(un)
            llp += np.log2(l1 * pun + l2 * pbi + l3 * ptri)
        return llp

    def interpolate(self, lam1, lam2, lam3, predict):
        """
        Interpolates the probabilities using the given lambda values and calculates the perplexity.
        """
        assert lam1 + lam2 + lam3 == 1
        llp = 0
        M = 0
        for sentence in predict:
            llp += self.calc_loglikelihoods(sentence=sentence, lams=(lam1,lam2,lam3))
            M += len(sentence) - 1
        avg_llp = (- 1. / M) * llp
        return 2. ** avg_llp
