import argparse
import pandas as pd
import numpy as np

def get_dialog(inp, mod):
    inp = inp['dialogue'].replace('<span class=participant_2>', '').replace('<span class=participant_1>', '').replace('</span>', '').replace('\r', '').replace('\n', '').split('<br />')
    out = [inp[0]]
    for i in inp[1:]:
        if i[:15]==out[-1][:15] and mod == 'join':
            out[-1] = out[-1] + ' ' + i[15:]
        elif i[:12] != 'Пользователь' and mod == 'join':
            out[-1] = out[-1] + ' ' + i
        else:
            out.append(i)
    out = [i.replace('Пользователь 1: ', '').replace('Пользователь 2: ', '') for i in out]
    return out

def proc_row(row, data, negs_n, out_file, mod):
    ind = row[0]
    row = row[1]
    dialog = get_dialog(row, mod=mod)
    with open(out_file, 'a') as outfile:
        for i in range(1, len(dialog)):
            context = dialog[:i]
            res = dialog[i]
            negs = dialog[i+1:][:negs_n]
            while len(negs) != negs_n:
                samp = data.sample().iloc[0]
                if samp.name != ind:
                    samp = np.random.choice(get_dialog(samp, mod=mod))
                    negs.append(samp)
            outfile.write('{}\t{}\t{}\n'.format(1, '\t'.join(context), res.strip()))
            for neg in negs:
                outfile.write('{}\t{}\t{}\n'.format(0, '\t'.join(context), neg.strip()))
        
    

def get_datasets(df, split_i, negs_n, mod, path='train.txt'):
    data = df.sample(len(df))
    if split_i != 0:
        train_path='{}/train.txt'.format(path)
        val_path='{}/dev.txt'.format(path)
        split_i = len(data)//split_i
        train = data[split_i:]
        val = data[:split_i]
    else:
        train_path='{}/split.txt'.format(path)
        val_path='{}/val.txt'.format(path)
        train = data
        val = data[:1]
    with open(train_path, 'w') as f:
        pass
    with open(val_path, 'w') as f:
        pass
    for row in train.iterrows():
        proc_row(row,train, negs_n, train_path, mod=mod)
    print(len(train))
    for row in val.iterrows():
        proc_row(row,train, negs_n, val_path, mod=mod)
    print(len(val))
    
parser = argparse.ArgumentParser()
parser.add_argument("--mod", default='join', type=str)
parser.add_argument("--path", default='toloka', type=str)
parser.add_argument("--negs", default=15, type=int)
parser.add_argument("--split", default=3, type=int)
args = parser.parse_args()
    
df = pd.read_csv('TlkPersonaChatRus/dialogues.tsv', delimiter='\t')
get_datasets(df, args.split, args.negs, path=args.path, mod=args.mod)
