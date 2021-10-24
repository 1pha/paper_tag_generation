import sys
import json
import logging

from transformers import HfArgumentParser, TrainingArguments
from transformers import AutoConfig, AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import (
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
)
from datasets import load_from_disk

from arguments import ModelArguments, DataArguments
from utils import set_seed


logger = logging.getLogger(__name__)


def main():

    # 0. Argument Setup
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    print(f"Use {model_args.model_name_or_path} model.")
    set_seed(training_args.seed)

    # logging 설정
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # verbosity 설정 : Transformers logger의 정보로 사용합니다 (on main process only)
    logger.info("Training/evaluation parameters %s", training_args)

    # 2. Load Model
    model_name = model_args.model_name_or_path
    config = AutoConfig.from_pretrained(model_name, cache_dir=None,)
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, cache_dir=None, use_fast=True,
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name, config=config, cache_dir=None,
    )

    # 1. Load Data
    tag_dataset = load_from_disk("./data/paperswithcode/")

    def preprocess(examples):

        tokenized_example = tokenizer(
            examples["title"],
            examples["abstract"],
            max_length=data_args.max_source_length,
            padding=data_args.padding,
            truncation=data_args.truncation,
        )

        label = tokenizer(
            [
                f"{area}, {' '.join(task_id.split('-'))}"
                for area, task_id in zip(examples["area"], examples["task_id"])
            ]
        )

        tokenized_example["labels"] = label["input_ids"]
        tokenized_example["id"] = examples["arxiv_id"]

        return tokenized_example

    if training_args.do_train:
        train_dataset = tag_dataset["train"]
        train_dataset = train_dataset.select(
            range(int(data_args.train_subsample_ratio * len(train_dataset)))
        )
        remove_columns = train_dataset.column_names
        train_dataset = train_dataset.map(
            preprocess,
            batched=True,
            remove_columns=remove_columns,
            desc="Preprocess Training Dataset",
        )

    if training_args.do_eval:
        eval_dataset = tag_dataset["dev"]
        eval_dataset = eval_dataset.select(
            range(int(data_args.valid_subsample_ratio * len(eval_dataset)))
        )

        remove_columns = eval_dataset.column_names
        eval_dataset = eval_dataset.map(
            preprocess,
            batched=True,
            remove_columns=remove_columns,
            desc="Preprocess Evaluation(dev) Dataset",
        )

    data_collator = DataCollatorForSeq2Seq(
        tokenizer, model=model, pad_to_multiple_of=None,
    )

    args = Seq2SeqTrainingArguments(
        output_dir=training_args.output_dir,
        do_train=training_args.do_train,
        do_eval=training_args.do_eval,
        predict_with_generate=True,
        per_device_train_batch_size=training_args.per_device_train_batch_size,
        per_device_eval_batch_size=training_args.per_device_eval_batch_size,
        num_train_epochs=training_args.num_train_epochs,
        save_strategy="steps",
        save_total_limit=10,  # 모델 checkpoint를 최대 몇개 저장할지 설정
        report_to="wandb",
        logging_steps=10,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset if training_args.do_train else None,
        eval_dataset=eval_dataset if training_args.do_eval else None,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    if training_args.do_train:

        train_result = trainer.train(resume_from_checkpoint=None)

        metrics = train_result.metrics
        metrics["train_samples"] = len(train_dataset)

        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)
        trainer.save_state()

    if training_args.do_eval:

        metrics = trainer.evaluate(
            max_length=data_args.max_target_length,
            num_beams=data_args.num_beams,
            metric_key_prefix="eval_bleu",
        )
        metrics["eval_samples"] = len(eval_dataset)

        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)

    if training_args.do_predict:

        def test_preprocess(examples):

            tokenized_example = tokenizer(
                examples["title"],
                examples["abstract"],
                max_length=data_args.max_source_length,
                padding=data_args.padding,
                truncation=data_args.truncation,
            )
            tokenized_example["labels"] = [
                [tokenizer.bos_token_id] for i in range(len(examples["arxiv_id"]))
            ]
            tokenized_example["id"] = examples["arxiv_id"]

            return tokenized_example

        test_dataset = tag_dataset["test"]
        remove_columns = test_dataset.column_names
        test_dataset = test_dataset.map(
            test_preprocess,
            batched=True,
            remove_columns=remove_columns,
            desc="Preprocess Test Dataset",
        )

        predictions = trainer.predict(
            test_dataset=test_dataset,
            max_length=data_args.max_target_length,
            num_beams=data_args.num_beams,
            metric_key_prefix="eval_bleu",
        )
        generated_tag = tokenizer.batch_decode(
            predictions.predictions, skip_special_tokens=True
        )
        prediction_path = f"{training_args.output_dir}/predictions.json"
        logger.info(f"Save test data predictions to {prediction_path}")
        with open(prediction_path, "w", encoding="utf-8") as writer:
            writer.write(
                json.dumps(
                    {k: v for k, v in zip(test_dataset["id"], generated_tag)},
                    indent=4,
                    ensure_ascii=False,
                )
                + "\n"
            )


if __name__ == "__main__":
    main()
