"""Observable-category first-order Markov analysis (not a full HMM)."""
from __future__ import annotations
import math
from collections import Counter

CATEGORIES=("ALPHA","DIGIT","DOT","SLASH","QUERY","SPECIAL","OTHER")

def tokenize(url: str):
    states=[]
    for c in url:
        if c.isalpha():state="ALPHA"
        elif c.isdigit():state="DIGIT"
        elif c==".":state="DOT"
        elif c=="/":state="SLASH"
        elif c in "?&=":state="QUERY"
        elif c in "- _@!~,+*#$%":state="SPECIAL"
        else:state="OTHER"
        states.append(state)
    return states

def analyze(url: str):
    states=tokenize(url);counts=Counter(zip(states,states[1:]));out={}
    for a,b in counts:
        out.setdefault(a,{})[b]=counts[a,b]
    # Add-one smoothing over the observed outgoing state set (or full vocabulary).
    probs={};transition_surprise=0.0
    for a,row in out.items():
        denom=sum(row.values())+len(CATEGORIES)
        probs[a]={b:(row.get(b,0)+1)/denom for b in CATEGORIES}
    for a,b in zip(states,states[1:]):
        transition_surprise-=math.log(probs[a][b])
    transitions=max(0,len(states)-1)
    initial_counts=Counter(states)
    initial_probs={state:(initial_counts[state]+1)/(len(states)+len(CATEGORIES)) for state in CATEGORIES} if states else {}
    initial_probability=initial_probs[states[0]] if states else 1.0
    log_probability=math.log(initial_probability)-transition_surprise
    probability=math.exp(log_probability) if log_probability>-700 else 0.0
    return {"categories":CATEGORIES,"sequence":states,"initial_state_probabilities":initial_probs,"transition_counts":{a:{b:int(v) for b,v in row.items()} for a,row in out.items()},"transition_probabilities":probs,"sequence_probability":float(probability),"mean_transition_surprise":float(transition_surprise/transitions) if transitions else 0.0,"description":"Within-URL add-one-smoothed first-order Markov descriptive score; no corpus-trained anomaly baseline and not a full Hidden Markov Model."}
