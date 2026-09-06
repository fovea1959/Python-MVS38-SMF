import logging

from aws_tape import *


class TapeFile:
    def __init__(self):
        self.blocks : list[TapeBlock] = []

    def append(self, tape_data: TapeBlock):
        self.blocks.append(tape_data)

    def len(self):
        return len(self.blocks)

    def __repr__(self):
        return "TapeFile: " + str(self.blocks)


class NLTape:
    def __init__(self, filename: str):
        self.tape_files : list[TapeFile] = list()

        self.tape_files.append(TapeFile())

        content: TapeBlock | TapeMark
        for content in read_aws_tape(filename):
            if isinstance(content, TapeMark):
                self.tape_files.append(TapeFile())
            else:
                self.tape_files[-1].append(content)

def main():
    import json
    nl_tape = NLTape("20260905-1046.aws")
    print(json.dumps(nl_tape.tape_files, indent=1, default=str))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()