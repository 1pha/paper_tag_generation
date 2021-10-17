from arguments import ModelArguments, DataArguments
from train import train
from transformers import HfArgumentParser, TrainingArguments


def main():

    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    print(model_args.model_name_or_path)

    if training_args.do_train:
        train()


if __name__ == "__main__":
    main()
