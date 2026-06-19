def load_tok_file(path):
    with path.open() as fin:
        for line in fin:
            yield line.split()

def load_tsv_file(path):
    with path.open() as fin:
        for line in fin:
            yield [s.split() for s in line.split('\t')]
