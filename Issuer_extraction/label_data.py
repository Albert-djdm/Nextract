# Author: Albert de Jamblinne de Meux
# thealbertsmail@gmail.com
# All right reserved.
#
# Under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License
# Read the LICENSE.TXT for detail or https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode


# to store and process data from the label

import os
import ordered_set
import csv


def merge_csv(files=('issuer.csv', 'guarantor.csv', 'roc.csv', 'zcp.csv', 'minTrad.csv', 'mltTrad.csv', 'optCur.csv'),
              tofile='final.csv'):
    '''
    Merge the different csv files into one file for submission.

    Args:
        files: a iterable with the data for issuer,guarantor,roc,zero coupon flag, min trade amount,
        multiple trade amount and operational currency. (in this order !)
        tofile: name of the file where the data are written.

    '''
    newd={}
    for file in files:
        with open(file,'r') as f:
            f = csv.reader(f)
            for item in f:
                if item[0] not in newd:
                    newd[item[0]]=[item[1]]
                else:
                    newd[item[0]].append(item[1])

    with open(tofile,'w') as f:
        writer = csv.writer(f,delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['ISIN','ISSUER.NAME','GA.NAME','ROC','ZCP.FL','MIN.TRAD.AMT','MLT.TRAD.AMT','OPS.CURR'])
        for item in newd:
            tmp = newd[item]
            tmp.insert(0,item)
            writer.writerow(tmp)

    print('Done')


def to_csv(filename, data):
    '''
    Save a set of data into a cvs file.

    Args:
        filename = name of the file where the data should be written.
        data = a dict with key == isin and string as value.
    '''
    with open(filename,'w') as f:
        writer = csv.writer(f,delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        for item in data:
            writer.writerow([item,data[item]])

class data(object):
    '''
    Store the data from the data set, this is the labels if available and the
    filesId (always).

    '''
    def __init__(self,folder='../Newdata/train/',):
        '''
        Create a new data class with the data imported.

        the data store in the object are store under the form of a dict.
        For each dict, the isin are the key and the values are orderedSet containing strings
        with the data. The set is empty if there are no label

        self.docid : document ids.
        self.guarantor : names of the guarantor
        self.issuer : names of the issuer
        self.zcp : zero coupon flag.
        self.minTrad : Minimum trade amount
        self.mltTrad : Min trade amount
        self.optCur : operational currency
        self.roc : required open cities.

        Args:
            folder: path to the root folder where the data are, the exact path for the
                    fileif and labels are hard coded from there, working for the training set (train)
                    intermediary test set (int_test) and final set (final_test).
        '''
        type = folder.strip('/').split('/')[-1]
        if type == 'train':
            docidf = os.path.join(folder,'docID/docid_train.csv')
            guarantorf = os.path.join(folder,'outcome/guarantor_train.csv')
            isinf = os.path.join(folder,'outcome/ISIN_train.csv')
            rocf = os.path.join(folder,'outcome/ROC_train.csv')
        elif type == 'int_test':
            docidf = os.path.join(folder,'docID/docid_int_test.csv')
            guarantorf = None
            isinf= None
            rocf = None
        elif type == 'final_test':
            docidf = os.path.join(folder,'docID/docid_final_test.csv')
            guarantorf = None
            isinf= None
            rocf = None

        else:
            raise ValueError('Only train and int_test folder can be use.')

        self.docid = {}
        self.guarantor = {}
        self.issuer = {}
        self.zcp = {} # zero coupon flag
        self.minTrad = {}
        self.mltTrad = {}
        self.optCur = {}
        self.roc = {}

        with open(docidf) as f:
            f=csv.reader(f)
            #line = f.next()
            next(f)
            for tmp in f:
                if tmp[1] in self.docid:
                    self.docid[tmp[1]].add(tmp[0])
                else:
                    self.docid[tmp[1]]=ordered_set.OrderedSet((tmp[0],))

        if guarantorf is not None:
            with open(guarantorf) as f:
                f = csv.reader(f)
                #line = f.next()
                next(f)
                for tmp in f:
                    if tmp[1] != '':
                        if tmp[0] in self.guarantor:
                            self.guarantor[tmp[0]].add(tmp[1])
                        else:
                            self.guarantor[tmp[0]]=ordered_set.OrderedSet((tmp[1],))
                    else:
                        self.guarantor[tmp[0]] = ordered_set.OrderedSet()

        if rocf is not None:
            with open(rocf) as f:
                f = csv.reader(f)
                #line = f.next()
                next(f)
                for tmp in f:
                    if tmp[1] != '':
                        if tmp[0] in self.roc:
                            self.roc[tmp[0]].add(tmp[1])
                        else:
                            self.roc[tmp[0]]=ordered_set.OrderedSet((tmp[1],))
                    else:
                        self.roc[tmp[0]] = ordered_set.OrderedSet()

        if isinf is not None:
            with open(isinf) as f:
                f = csv.reader(f)
                #line = f.next()
                next(f)
                for tmp in f:
                    if tmp[0] in self.issuer:
                        self.issuer[tmp[0]].add(tmp[1])
                    else:
                        self.issuer[tmp[0]]=ordered_set.OrderedSet((tmp[1],))

                    if tmp[0] in self.zcp:
                        self.zcp[tmp[0]].add(tmp[2])
                    else:
                        self.zcp[tmp[0]] = ordered_set.OrderedSet((tmp[2],))

                    if tmp[0] in self.minTrad:
                        self.minTrad[tmp[0]].add(tmp[3])
                    else:
                        self.minTrad[tmp[0]] = ordered_set.OrderedSet((tmp[3],))

                    if tmp[0] in self.mltTrad:
                        self.mltTrad[tmp[0]].add(tmp[4])
                    else:
                        self.mltTrad[tmp[0]] = ordered_set.OrderedSet((tmp[4],))

                    if tmp[0] in self.optCur:
                        self.optCur[tmp[0]].add(tmp[5])
                    else:
                        self.optCur[tmp[0]] = ordered_set.OrderedSet((tmp[5],))

        self.torm=set()
        if guarantorf is not None:
            for isin in self.docid:
                if isin not in self.guarantor:
                    self.torm.add(isin)

                if isin not in self.issuer:
                    self.torm.add(isin)

                if isin not in self.zcp:
                    self.torm.add(isin)

                if isin not in self.minTrad:
                    self.torm.add(isin)

                if isin not in self.mltTrad:
                    self.torm.add(isin)

                if isin not in self.optCur:
                    self.torm.add(isin)

                if isin not in self.roc:
                    self.torm.add(isin)

        for item in self.torm:
            del self.docid[item]


def test(prediction, answer):
    '''
    Simple test of the prediction. Print the error in %.

    No fuzzy matching !!!! if a pipe ('|') is in the string,
    the string is split and a value is considered as correct if
    all the values in the both the prediction and answer are the
    same (independently of the order).

    prediction, answer: dic with isin as key and strings as values.

    '''
    total = float(len(answer))
    err = 0.0
    notcomp = 0.0
    for item in answer:
        if item in prediction:
            if set(prediction[item].split('|')) != set(answer[item].split('|')) :
                err += 1
                print item, ' | ', prediction[item], ' | ', answer[item]
        else:
            notcomp += 1

    print
    print('total number of set compared: ' + str(total))
    print('total number of missing set: ' + str(notcomp))
    print('error %: ' + str(err / total * 100))
