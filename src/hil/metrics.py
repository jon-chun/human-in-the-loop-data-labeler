from __future__ import annotations
from typing import List, Dict

def confusion_binary(y_true: List[bool], y_pred: List[bool]):
    tp=fp=fn=tn=0
    for t,p in zip(y_true,y_pred):
        if t and p: tp+=1
        elif not t and p: fp+=1
        elif t and not p: fn+=1
        else: tn+=1
    return tp,fp,fn,tn

def metrics_binary(y_true: List[bool], y_pred: List[bool]) -> Dict:
    tp,fp,fn,tn = confusion_binary(y_true, y_pred)
    total = tp+fp+fn+tn
    acc = (tp+tn)/total if total else 0.0
    prec_pos = tp/(tp+fp) if (tp+fp) else 0.0
    rec_pos  = tp/(tp+fn) if (tp+fn) else 0.0
    f1_pos   = (2*prec_pos*rec_pos)/(prec_pos+rec_pos) if (prec_pos+rec_pos) else 0.0
    prec_neg = tn/(tn+fn) if (tn+fn) else 0.0
    rec_neg  = tn/(tn+fp) if (tn+fp) else 0.0
    f1_neg   = (2*prec_neg*rec_neg)/(prec_neg+rec_neg) if (prec_neg+rec_neg) else 0.0
    return {
        "accuracy": acc,
        "recall_pos": rec_pos, "f1_pos": f1_pos,
        "recall_neg": rec_neg, "f1_neg": f1_neg,
        "confusion": {"tp":tp,"fp":fp,"fn":fn,"tn":tn}
    }

def confusion_ab(y_true: list[str], y_pred: list[str]):
    taa=tab=tba=tbb=0
    for t,p in zip(y_true,y_pred):
        if t=="a" and p=="a": taa+=1
        elif t=="a" and p=="b": tab+=1
        elif t=="b" and p=="a": tba+=1
        elif t=="b" and p=="b": tbb+=1
    return taa,tab,tba,tbb

def metrics_ab(y_true: list[str], y_pred: list[str]) -> Dict:
    taa,tab,tba,tbb = confusion_ab(y_true,y_pred)
    total = taa+tab+tba+tbb
    acc = (taa+tbb)/total if total else 0.0
    tp_a, fn_a, fp_a = taa, tab, tba
    prec_a = tp_a/(tp_a+fp_a) if (tp_a+fp_a) else 0.0
    rec_a  = tp_a/(tp_a+fn_a) if (tp_a+fn_a) else 0.0
    f1_a   = (2*prec_a*rec_a)/(prec_a+rec_a) if (prec_a+rec_a) else 0.0
    tp_b, fn_b, fp_b = tbb, tba, tab
    prec_b = tp_b/(tp_b+fp_b) if (tp_b+fp_b) else 0.0
    rec_b  = tp_b/(tp_b+fn_b) if (tp_b+fn_b) else 0.0
    f1_b   = (2*prec_b*rec_b)/(prec_b+rec_b) if (prec_b+rec_b) else 0.0
    return {
        "accuracy": acc,
        "recall_a": rec_a, "f1_a": f1_a,
        "recall_b": rec_b, "f1_b": f1_b,
        "confusion": {"a_to_a":taa,"a_to_b":tab,"b_to_a":tba,"b_to_b":tbb}
    }
