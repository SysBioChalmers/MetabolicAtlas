import os

def get_metadata(file):
    try:
        header = []
        with open(file, 'r') as fh:
            for line in fh:
                line = line.strip()
                if not line or line[0] == "#":
                    continue
                arr = line.split('\t')
                if line[0] == "@":
                    header = arr
                    header[0] = header[0][1:]
                break
    except Exception as e:
        print(e)
        exit(1)
    return header

def file_to_dicts_values(file):
    try:
        l = []
        IDs = set()
        with open(file, 'r') as fh:
            header = []
            for line in fh:
                line = line.strip()
                if not line or line[0] == "#":
                    continue
                arr = line.split('\t')
                if line[0] == "@":
                    header = arr
                    header[0] = header[0][1:]
                else:
                    new_d = dict(zip(header, arr))
                    if 'ID' not in new_d or not new_d['ID']:
                        print ("Error: ID key not found or empty when parsing annotation file")
                        exit(1)
                    if new_d['ID'] in IDs:
                        print ("Error: duplicate ID '%s'" % new_d['ID'])
                        exit(1)
                    l.append(new_d)
    except Exception as e:
        print(e)
        exit(1)
    return l


def write_dicts_to_file(list_dicts, file):
    if not os.path.isfile(file):
        print ("Error: file '%s' not found")
        exit(1)

    lines = []
    with open(file, 'r') as fh:
        lines = []
        header = []
        # save header, comments etc..
        for line in fh:
            line = line.strip()
            if not line or line[0] == "#":
                lines.append(line)
                continue
            arr = line.split('\t')
            if line[0] == "@":
                lines.append(line)
                header = arr
                header[0] = header[0][1:]

        for row_dict in list_dicts:
            lines.append("\t".join([row_dict[c] if c in row_dict else '' for c in header]))

    if lines:
        with open(file, 'w') as fw:
            fw.write('\n'.join(lines))


def merge_values(file, dict_values_dicts):
    list_dicts = file_to_dicts_values(file)
    new_dicts_list = []
    contains_ID = set()
    # read the row data in the file in order
    for d in list_dicts:
        ID = d['ID']
        if ID not in dict_values_dicts:
            continue
        else:
            # merge dicts_values and dict_file
            dict_values_dicts[ID].pop('ID', None)  # prevent changing the ID
            d.update(dict_values_dicts[ID])
        contains_ID.add(ID)

    # add new annotations, for ID not already in the file
    for ID, d in dict_values_dicts.items():
        if ID in contains_ID:
            continue

        d.pop('ID', None)  # prevent changing the ID
        d['ID'] = ID
        list_dicts.append(d)  # might not contains all the headercolumns

    return list_dicts


