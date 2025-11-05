import argparse
import pathlib

import torch

def get_sequence_neg_log_probs(file):
    neg_log_probs = torch.load(file, map_location='cpu')
    return torch.stack([
        torch.sum(word_neg_log_probs)
        for word_neg_log_probs in neg_log_probs
    ])

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('right', type=pathlib.Path)
    parser.add_argument('wrong', type=pathlib.Path)
    args = parser.parse_args()

    right_neg_log_probs = get_sequence_neg_log_probs(args.right)
    wrong_neg_log_probs = get_sequence_neg_log_probs(args.wrong)
    mean_ratio = torch.mean(wrong_neg_log_probs - right_neg_log_probs)
    print(mean_ratio.item())

if __name__ == '__main__':
    main()
