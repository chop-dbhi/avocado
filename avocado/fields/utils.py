from django.utils.datastructures import SortedDict

def normalize_raw_data_for_avocado(raw_data):
    "Takes the `raw_data' (a QueryDict object) and normalizes it."
    sorted_dict = SortedDict({})

    for key, val in raw_data.lists():
        l = key.split('-')
        pk, kind = l[0], l[1]

        # test for multiple input fields i.e. `f20-value_0'
        if kind.startswith('value'):
            kind = kind[:5]

        if pk not in sorted_dict.keys():
            sorted_dict.update({pk: {'val': [], 'op': ''}})

        if kind == 'value':
            sorted_dict[pk]['val'].extend(val)
        elif kind == 'operator':
            sorted_dict[pk]['op'] = val[0]

        sorted(sorted_dict[pk]['val']) # HACK: ensure lexicographical
    return sorted_dict