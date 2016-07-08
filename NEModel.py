#
# Author: Albert de Jamblinne de Meux
# thealbertsmail@gmail.com
# All right reserved.
#
# Under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License
# Read the LICENSE.TXT for detail or https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
# 
#
import re
import numpy as np
import ordered_set
import numpy as np
from collections import defaultdict
import copy
import cPickle as pickle

class matcher(object):
    '''
    This object implement a special kind of fuzzy matching based on a reference set
    of data and on the order of the word.

    The goal is the match a name (composed of several word), or short sentences with a set of a reference data.
    Spelling madder ! Misspelling is not handel (Test of use of fuzzy matching did not bring good results...)
    '''

    def __init__(self, values, synonymes):
        '''

        Args:
            values: list with all the names of interest
            synonymes: list of pair of word that link a word or a sequence from the
                        name to match to the reference name.
        '''
        self.values = ordered_set.OrderedSet(values)
        self.synonymes = ordered_set.OrderedSet()
        for item in synonymes:
            self.synonymes.add((self.clean_string(item[0]),self.clean_string(item[1])))
        #self.ponctuation = '().,:!?\'%*-_&@$;[]{}'

        # create a vocabulary.
        self.vocab = ordered_set.OrderedSet()
        for item in values:
            # remove punctuation and lower case
            tmp = self.clean_string(item)
            for voc in tmp.split():
                if len(voc) > 0: # do not add empty string
                    self.vocab.add(voc)

        self.Lookup = dict()  # for fast retrieval of the index
        for x in xrange(0, len(self.vocab)):
            self.Lookup[self.vocab[x]] = x

        self.vector = [] # number form of each name
        self.l = [] # len of the each name
        for item in values:
            v, l = self.to_numberset(item)
            self.vector.append(v)
            self.l.append(l)

        # compute k values for the computation of the probability
        self.sumkVal = []
        for item in self.vector:
            self.sumkVal.append(self._sumk(item))

    def get_subsets(self, valueSet):
        '''

        Get all the subset of a list

        Return a dict with key the size of the sets, the values are sets of tuples
            that are ordered subset of the provided set.
        '''
        assert isinstance(valueSet,list) or isinstance(valueSet,tuple), 'valueSet must be a list or a tuple !'

        result = defaultdict(ordered_set.OrderedSet)
        ll = len(valueSet)
        for y in xrange(0, ll):
            for x in xrange(y, ll):
                if x == y:
                    result[x - y + 1].add((valueSet[x],))
                else:
                    tmp = list(result[x - y][-1])
                    tmp.append(valueSet[x])
                    result[x - y + 1].add(tuple(tmp))
        return result

    def clean_string(self,s):
        '''
        Clean the string. Remove ponctuation, lower the case and remove line break
        '''
        s = s.lower()
        s = s.replace('&',' and ')
        s = s.replace('@', ' at ')
        s = s.replace('%', ' percent ')
        s = s.replace('$', ' dolar ')
        s = ' '+s+' '
        for item in [' of ', ' the ', ' i ', ' not ', ' and ', ' to ', ' an ', ' a ', ' in ', ' for ', ' on ', ' at ']:
            s = s.replace(item, ' ')
        s = re.sub("[^a-zA-Z0-9\s]",
                      "",
                      s)

        s = s.replace('\n', ' ').replace('\r', '')
        return re.sub('\s+',' ',s) # remove multiple space...

    def to_numberset(self, words):
        '''
        Transform the string into number.

        Return a number set version of the string. Each word is replace by a number
        which is the position of this word in vocab. if the word is not in the vocab,
        -1 is put. Then return the set of number.

        Return set of number, word length of the string.
        '''
        result = []
        l = 0.0
        tmp = self.clean_string(words)
        for w in tmp.split():
            if len(w) > 0:
                l += 1.0
                if w in self.Lookup:
                    result.append(self.Lookup[w])
                else:
                    result.append(-1)

        x = 0
        while len(result) > x + 1:
            if result[x] == result[x + 1] == -1:
                result.pop(x)
            else:
                x += 1

        return self.get_subsets(result), l

    def _sumk(self, sets):
        '''
        Compute k sum value.
        '''
        r = 0.0
        for k in sets:
            r += k ** 2.0 * len(sets[k])
        return float(r)

    def get_Ps_vect(self, toTest, l=None):
        '''
        Get all the probabilities that the provided vector match with a words of self.values.
        '''
        result = []
        if l is None:
            l = float(max(toTest.keys()))

        for x in xrange(0, len(self.vector)):
            newset = dict()
            for k in self.vector[x]:
                newset[k] = set(self.vector[x][k]).intersection(toTest[k])
            ksum = self._sumk(newset)
            if l > 0.0:
                ll = self.l[x] / l
                if ll > 1.0:
                    ll = 1.0 / ll
                result.append(ksum / self.sumkVal[x] * ll)
            else:
                result.append(0.0)

        return result

    def get_Ps(self, words):
        '''
        Get all the probabilities that the provided words match witch a words of the self.values.
        '''
        result = []
        toTest, l = self.to_numberset(words)
        return self.get_Ps_vect(toTest, l)

    def get_alt(self, words):
        '''
        Provide all the alternative string to the provided one obtained by substitution of
        word in self.synonymes
        '''
        words = self.clean_string(words)

        result = set((words,))
        for sym in self.synonymes:
            if sym[0] in words:
                result.add(words.replace(sym[0], sym[1]))

        return result

    def closerMatch(self, words):
        '''
        Provide the entry that match the closest

        Return: matching probability, matched value.
        '''
        res = []
        for w in self.get_alt(words):
            r = self.get_Ps(w)
            idx = np.argmax(r)
            res.append((r[idx], self.values[idx]))

        res = sorted(res, reverse=True)

        return res[0]

    def save(self, filename):
        '''
        Save the object into the file

        Args:
            filename: path to the file to write in.
        '''
        with open(filename, 'wb') as output:
            pickle.dump(self, output)

    @classmethod
    def from_file(cls, filename):
        '''
        Reopen a saved object

        Args:
            filename: path to the file to read
        '''
        with open(filename, 'rb') as pkl_file:
            return pickle.load(pkl_file)


class extractor(object):
    '''
    Defined an extractor to extract data from a text.
    '''

    def __init__(self, matcher, beforFlag, afterFlag, removeFlag ,globalre=None,start=None):
        '''
        Create a new extractor model.
        Args:
            start: (string) first anotation of the model, by default: Nothing.
            matcher: a matcher object for the matching of the string to extract.
            beforFlag: list of strings indicating that the word to extract probably before this string
            afterFlag: list of strings indicating that the word to extract probably after this string
            removeFlag: list of string indicating the the words after this flag are to be remove (ignored)
            globalre: list of global replacement, Allow to replace a given string everywhere in the text
             in a given string is found in the text. This may be usfull because some company specific location
             are not always close to where the issuer is matched. These are tuples: (what to match, what to replace, by what)
        '''
        assert isinstance(start,str)
        if start is not None:
            self.start = [start]
        else:
            self.start = []

        self.matcher = matcher
        self.beforFlag = [matcher.clean_string(item) for item in beforFlag]
        self.afterFlag =  [matcher.clean_string(item) for item in afterFlag]
        self.removeFlag =  [matcher.clean_string(item) for item in removeFlag]
        self.globalre = []
        if globalre is not None:
            for item in globalre:
                self.globalre.append((matcher.clean_string(item[0]),matcher.clean_string(item[1]),matcher.clean_string(item[2])))

    def extract(self, txt):
        '''
        Extract the data from the text.

        Args:
            txt: the text from which the data should be extracted.
        '''

        # Pre-process the text.
        txt = self.matcher.clean_string(txt)

        # global replace.
        for item in self.globalre:
            if item[0] in txt:
                txt = txt.replace(item[1],item[2])
        #print txt

        # First create a simplified representation of the text.
        v = copy.deepcopy(self.start)

        # Create alternative texts based on the synonyms
        newtxt=set((txt,))
        for item in self.matcher.synonymes:
            newtxt.add(txt.replace(item[0], item[1]))

        txtc=''
        for item in newtxt:
            txtc+=item

        for item in self.beforFlag:
            txtc = txtc.replace(item,' - '+item)

        for item in self.afterFlag:
            txtc = txtc.replace(item,item+' + ')

        for item in self.removeFlag:
            txtc = txtc.replace(item, item + ' * ')

        txtc = re.sub('(-\s*){1,}', ' - ', txtc)

        # tokenize the text with n-grams...
        txtc = txtc.split()
        #print txtc
        #print '======================================'
        tmp = [] # for subset
        for x in xrange(0, len(txtc)):
            if txtc[x] in self.matcher.Lookup:
                tmp.append(self.matcher.Lookup[txtc[x]])
            else: # not in a group
                if txtc[x] in ['+', '*', '-']: # if we get a flag
                    if txtc[x] == '-' and not isinstance(v[-1], int):
                        v.append(0)
                    v.append(txtc[x])
                    if txtc[x] == '+':
                        v.append(0)
                else:
                    if len(tmp) > 0:
                        v.append(tmp)
                        v.append(-1)
                        tmp = []
                    elif isinstance(v[-1], int): # if there is a space value, increase it
                        v[-1] -= 1
                    else:
                        v.append(-1) # if not add one.

        #print v
        #print '======================================'

        # parse the text
        group = set() # set of group of words of interest
        x = 0
        while x < len(v):
            if v[x] == '*' and x + 2 < len(v):  # if * is encountered, skip the 2 next values
                x += 2
                continue
            if v[x] == '-' and x > 2: # flag,
                group.add((abs(v[x - 1]), tuple(v[x - 2])))
            if v[x] == '+' and x + 2 < len(v):
                if isinstance(v[x + 1], int):
                    group.add((abs(v[x + 1]), tuple(v[x + 2])))
                else:
                    if isinstance(v[x + 2], int):
                        group.add((abs(v[x + 2]), tuple(v[x + 3])))
                    else:
                        group.add((0, tuple(v[x + 2])))
            x += 1

        #print group
        #print '======================================'

        # now we match each of these group with the matcher and get probability values
        r = []
        x = 0
        for item in group:
            subset = self.matcher.get_subsets(item[1])
            ps = self.matcher.get_Ps_vect(subset)
            idx = np.argmax(ps)
            # print x,fcomp.values[idx], ps[idx]/float(item[0]+1)*len(fcomp.values[idx].split()),item[0]
            x += 1
            # (probability of being good, value matched)
            # being good = match probability / distance with the flag * length of the matched string
            # what we look must be close to the flag, and as long a possible.
            r.append((ps[idx] / float(item[0] + 1) * len(self.matcher.values[idx].split()), self.matcher.values[idx]))

        # sort all the results
        #print r
        r = sorted(r, key=lambda x: x[0], reverse=True)

        #print r
        #print '======================================'
        # get the best match.
        if len(r) > 0:
            return r[0][1]
        else:
            return None

    def save(self, filename):
        '''
        Save the object into the file

        Args:
            filename: path to the file to write in.
        '''
        with open(filename, 'wb') as output:
            pickle.dump(self, output)

    @classmethod
    def from_file(cls, filename):
        '''
        Reopen a saved object

        Args:
            filename: path to the file to read
        '''
        with open(filename, 'rb') as pkl_file:
            return pickle.load(pkl_file)
