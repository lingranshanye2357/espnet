#!/usr/bin/env python3
from espnet2.tasks.vspeechlm import VSpeechLMTask


def get_parser():
    parser = VSpeechLMTask.get_parser()
    return parser


def main(cmd=None):
    """VSpeech LM training.

    Example:

        % python vspeechlm_train.py --print_config --optim adadelta
        % python vspeechlm_train.py --config conf/train.yaml
    """
    VSpeechLMTask.main(cmd=cmd)


if __name__ == "__main__":
    main()
