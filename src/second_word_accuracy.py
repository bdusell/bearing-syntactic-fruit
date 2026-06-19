import argparse
import pathlib

import torch

from load_util import load_tok_file, load_tsv_file

def second_word_matches(a, b):
    if len(b) < 2:
        raise ValueError
    return len(a) >= 2 and a[1] == b[1]

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('samples', type=pathlib.Path)
    parser.add_argument('references', type=pathlib.Path)
    args = parser.parse_args()

    samples = load_tsv_file(args.samples)
    references = load_tok_file(args.references)
    result = torch.mean(torch.tensor([
        [second_word_matches(sample, reference) for sample in sample_list]
        for sample_list, reference in zip(samples, references)
    ], dtype=torch.float))
    print(result.item())

if __name__ == '__main__':
    main()
