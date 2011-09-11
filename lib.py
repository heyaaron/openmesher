def nested_dict_merge(d1,d2):
    merged = d1.copy()
    for k,v in d2.iteritems():
        if merged.has_key(k):
            if type(merged[k]) is dict:
                merged[k] = nested_dict_merge(merged[k], v)
            else:
                raise KeyError('Collision in key %s type %s' %(k, type(merged[k])))
        else:
            merged[k] = v
    return merged
