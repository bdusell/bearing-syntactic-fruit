import argparse
import pathlib

import torch

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('cross_entropy_file', type=pathlib.Path)
    args = parser.parse_args()

    # Read the first -log probability for each sequence, convert them to
    # probabilities, and average them.
    ce = torch.stack([x[0] for x in torch.load(args.cross_entropy_file)])
    probs = torch.exp(-ce)
    mean = torch.mean(probs)
    print(mean.item())

if __name__ == '__main__':
    main()
