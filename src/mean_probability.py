import argparse
import json
import pathlib
import sys

import torch

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('negative_log_probabilities', type=pathlib.Path)
    args = parser.parse_args()

    neg_log_probs = torch.load(args.negative_log_probabilities, map_location='cpu')
    num_predictions = torch.sum(torch.tensor([len(s) for s in neg_log_probs]))
    sequence_neg_log_probs = torch.stack([
        torch.sum(word_neg_log_probs)
        for word_neg_log_probs in neg_log_probs
    ])
    micro_averaged_ce = torch.sum(sequence_neg_log_probs) / num_predictions
    mean_sequence_prob = torch.mean(torch.exp(-sequence_neg_log_probs))
    json.dump(dict(
        cross_entropy_per_token=micro_averaged_ce.item(),
        mean_sequence_probability=mean_sequence_prob.item()
    ), sys.stdout)

if __name__ == '__main__':
    main()
