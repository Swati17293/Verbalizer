from models.ngram import ngram_probs
import gzip, os, re, sys
from math import log

"""
Probabilistically split concatenated words using NLP
Part of code was taken from https://github.com/keredson/wordninja
"""
class SplitWords(object):
    @classmethod
    def split(cls, s):
        # Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'dictionary/ontology.txt'), encoding='cp1252') as f:
            words = f.read().split()
        cls._wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
        cls._maxword = max(len(x) for x in words)
        _SPLIT_RE = re.compile("[^a-zA-Z0-9']+")

        """Uses dynamic programming to infer the location of spaces in a string without spaces."""
        l = [cls._split(x) for x in _SPLIT_RE.split(s)]
        return [item for sublist in l for item in sublist]

    @classmethod
    def _split(cls, s):
        # Find the best match for the i first characters, assuming cost has
        # been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length).
        def best_match(i):
            candidates = enumerate(reversed(cost[max(0, i-cls._maxword):i]))
            return min((c + cls._wordcost.get(s[i-k-1:i].lower(), 9e999), k+1) for k,c in candidates)

        # Build the cost array.
        cost = [0]
        for i in range(1,len(s)+1):
            c,k = best_match(i)
            cost.append(c)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(s)
        while i>0:
            c,k = best_match(i)
            assert c == cost[i]
            # Apostrophe and digit handling (added by Genesys)
            newToken = True
            if not s[i-k:i] == "'": # ignore a lone apostrophe
                if len(out) > 0:
                    # re-attach split 's and split digits
                    if out[-1] == "'s" \
                    or (s[i-1].isdigit() and out[-1][0].isdigit()): # digit followed by digit
                        out[-1] = s[i-k:i] + out[-1] # combine current token with previous token
                        newToken = False
            # (End of Genesys addition)

            if newToken:
                out.append(s[i-k:i])

            i -= k

        return reversed(out)


"""
Split German compound words
Part of was taken from https://github.com/dtuggener/CharSplit
ngram_probs.py file is used to split the text
"""
class CharSplit(object):
    @classmethod
    def split_compound(cls, word: str):
        """
        Return list of possible splits, best first
        :param word: Word to be split
        :return: List of all splits
        """

        word = word.lower()

        # If there is a hyphen in the word, return part of the word behind the last hyphen
        if '-' in word:
            return [[1., word.title(), re.sub('.*-', '', word.title())]]
        
        scores = [] # Score for each possible split position
        # Iterate through characters, start at forth character, go to 3rd last
        for n in range(3, len(word)-2):

            pre_slice = word[:n]
            
            # Cut of Fugen-S
            if pre_slice.endswith('ts') or pre_slice.endswith('gs') or pre_slice.endswith('ks') \
                    or pre_slice.endswith('hls') or pre_slice.endswith('ns'):
                if len(word[:n-1]) > 2: pre_slice = word[:n-1]

            # Start, in, and end probabilities
            pre_slice_prob = []
            in_slice_prob = []
            start_slice_prob = []
            
            # Extract all ngrams
            for k in range(len(word)+1, 2, -1):
            
                # Probability of first compound, given by its ending prob
                if pre_slice_prob == [] and k <= len(pre_slice):
                    end_ngram = pre_slice[-k:]  # Look backwards
                    pre_slice_prob.append(ngram_probs.suffix.get(end_ngram, -1))    # Punish unlikely pre_slice end_ngram
                        
                # Probability of ngram in word, if high, split unlikely
                in_ngram = word[n:n+k]
                in_slice_prob.append(ngram_probs.infix.get(in_ngram, 1)) # Favor ngrams not occurring within words
                                    
                # Probability of word starting
                if start_slice_prob == []:
                    ngram = word[n:n+k]
                    # Cut Fugen-S
                    if ngram.endswith('ts') or ngram.endswith('gs') or ngram.endswith('ks') \
                            or ngram.endswith('hls') or ngram.endswith('ns'):
                        if len(ngram[:-1]) > 2:
                            ngram = ngram[:-1] 
                    start_slice_prob.append(ngram_probs.prefix.get(ngram, -1))

            if pre_slice_prob == [] or start_slice_prob == []: continue
            
            start_slice_prob = max(start_slice_prob)
            pre_slice_prob = max(pre_slice_prob)    # Highest, best preslice
            in_slice_prob = min(in_slice_prob)      # Lowest, punish splitting of good ingrams                               
            score = start_slice_prob - in_slice_prob + pre_slice_prob
            scores.append([score, word[:n].title(), word[n:].title()])

        scores.sort(reverse=True)
        if scores == []:
            scores=[ [0, word.title(), word.title()] ]
        return sorted(scores, reverse = True)[0]
    
    @classmethod
    def SplitCompoundWord(cls, word):
        splitAnswer = cls.split_compound(word)
        if splitAnswer[0] < 0.5:
            return word
        else:
            return splitAnswer[1:]