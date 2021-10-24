from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelArguments:

    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune from.
    """

    model_name_or_path: str = field(
        default="facebook/bart-base",
        metadata={
            "help": "Path to pretrained model or model identifier from huggingface.co/models"
        },
    )
    config_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained config name or path if not the same as model_name"
        },
    )
    tokenizer_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained tokenizer name or path if not the same as model_name"
        },
    )


@dataclass
class DataArguments:

    """
    For Data
    """

    train_subsample_ratio: float = field(
        default=1,
        metadata={
            "help": "Subsampling ratio of the training set, in order to reduce training time."
        },
    )
    valid_subsample_ratio: float = field(
        default=1,
        metadata={
            "help": "Subsampling ratio of the valid set, in order to reduce inference time."
        },
    )
    max_source_length: int = field(
        default=512, metadata={"help": "Controls input source length."}
    )
    max_target_length: int = field(
        default=8,
        metadata={"help": "Maximum length for generation. No need to be long."},
    )
    padding: bool = field(
        default=True,
        metadata={"help": "Flag to add padding after inputs being tokenized."},
    )
    truncation: bool = field(
        default=False,
        metadata={
            "help": "Whether to use first part of the sequence if longer than maximum"
        },
    )
    num_beams: int = field(
        default=2,
        metadata={
            "help": "Number of beams to be used in the beam search during generation."
        },
    )

