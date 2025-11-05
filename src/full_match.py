import argparse
import pathlib
import sys

def load_file(path):
    with path.open() as fin:
        for line in fin:
            yield line.split()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('hypotheses', type=pathlib.Path)
    parser.add_argument('references', type=pathlib.Path)
    args = parser.parse_args()

    num_full_match = 0
    num_examples = 0
    for hypothesis, reference in zip(
        load_file(args.hypotheses),
        load_file(args.references),
        strict=True
    ):
        num_full_match += int(hypothesis == reference)
        num_examples += 1
    accuracy = num_full_match / num_examples
    print(accuracy)

if __name__ == '__main__':
    main()
