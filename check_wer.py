#!/usr/bin/python

from wer import *

REF='test.ref.txt'
NBEST='test.txt'
TOP_N=10
DEBUG=False

def load_nbest_lists(file):
    """loads nbest lists into a dictionary. Each entry in the dictionary
    has an utterance id as key, and a list of transcriptions in the value 
    the transcriptions are sorted from most to least likely"""
    cutt=''
    nbest={}
    with open(file,'rt') as fin:
        for line in fin:
            if line.strip()=='': continue
            words=line.strip().split();
            if words[1] == '[':  # first entry
                cutt = words[0]
                transcript=' '.join(words[2:])
            elif words[-1] == ']': # last nbest entry for this utterance
                transcript=' '.join(words[0:-1])
            else:
                transcript=' '.join(words)
            # put this transcription in the data
            if cutt not in nbest: nbest[cutt] = []
            nbest[cutt].append(transcript)
    return nbest

def print_nbest_list(nbest):
    for k in nbest:
        for l in nbest[k]:
            print "%s -- %s" % (k,l)


def load_ref_list(file):
    refs={}
    fin=open(file,'rt')
    for line in fin:
        words=line.strip().split();
        refs[words[0]] = ' '.join(words[1:])
    return refs


def prune_nbest(nbest,amount):
    new_nbest={}
    for k in nbest:
        new_nbest[k] = nbest[k][0:amount]
    return new_nbest 

    
# read in the data
nbest=load_nbest_lists(NBEST);
refs=load_ref_list(REF);

# prune the nbest list
new_nbest = prune_nbest(nbest,TOP_N);
total_S = 0
total_I = 0
total_D = 0
total_N = 0
for k in nbest.keys():
    if (k in refs) and (k in new_nbest):
        best = -1
        # find the entry with the closest match to reference
        for j in range(len(new_nbest[k])):
            (S,I,D) = compute_SID(refs[k],nbest[k][j],DEBUG)
            #print "-- %i, %i %i" % (S,I,D)
            if best == -1 or S+I+D<best[0]+best[1]+best[2]:
                best=(S,I,D)
                best_j=j
                #print "THE BEST",best
        if DEBUG:
            print "best_j %i" % best_j
            print "REF: ", refs[k]
            print "HYP: ", nbest[k][best_j]
        # add that to the total scores
        total_S=total_S+best[0]
        total_I=total_I+best[1]
        total_D=total_D+best[2]
        total_N=total_N+len(refs[k].split())

# word error rate
wer = float((total_S + total_I + total_D))*100.0 / float(total_N)
print "Best WER = %.3f %i %i %i " % (wer,total_S,total_I,total_D)


