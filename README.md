2021 Fall XAI606 Project Proposal Baseline | 2020010429 Daehyun Cho

# Paper Title + Abstract to Tag Generation Task

From [paperswithcode](https://paperswithcode.com/sota), researchers are provided with SOTA models of numerous different tasks at once, also with their work written in paper. Thanks to sharing this tough organizing work, people studying artificial intelligence are now able to access and search with less labour compared to the past. Here in this work, I thought it would be good to use this archived papers once again for further usage.

Paperswithcode archived all papers in the following schema. 
```
nn_arxiv                                          
├─ paper_clf                                      
│  ├─ arguments.py                        
│  ├─ run.py                              
│  └─ utils.py                            
├─ data                                   
│  ├─ paperswithcode                      
│  │  ├─ train                            
│  │  │  ├─ dataset.arrow                 
│  │  │  ├─ state.json                    
│  │  │  └─ dataset_info.json         
│  │  ├─ dev                              
│  │  │  ├─ dataset.arrow                 
│  │  │  ├─ state.json                    
│  │  │  └─ dataset_info.json  
│  │  ├─ test                             
│  │  │  ├─ dataset.arrow                 
│  │  │  ├─ state.json                    
│  │  │  ├─ dataset_info.json   
│  │  │  └─ dataset_info.json   
│  │  └─ dataset_dict.json                
│  └─ arxiv                                                
├─ paper_mlm                              
│  └─ run.py                     
└─ README.md                              
```

## Generation-based Paper category prediction
All files inside `paper_clf`.

1. To train generation-based prediction, type in below
   ```
   python paper_clf/run.py --do_train --output_dir=finetuned_model
   ```
   + Use `train_subsample_ratio` from 0 to 1, if you want to use some portion of the training data.
   + `output_dir` is should be filled in. You can use this as a checkpoint for validation and evaluation.
   + Read `paper_clf/arguments.py` for detailed configuration.
   + Fill in pretrained model `model_name_or_path` with generation model. Recently Huggingface
2. To evaluate with evaluation data (dev), type in below
   ```
   python paper_clf/run.py --do_eval --model_name_or_path=finetuned_model --output_dir=finetuned_model
   ```
   + Use `valid_subsample_ratio` from 0 to 1, if you want to use some portion of the evaluation data.
   + Put the saved/trained model directory in `model_name_or_path` to use finetuned model that you have trained.
3. To make predictions with test data
    ```
    python paper_clf/run.py --do_predict --model_name_or_path=finetuned_model --output_dir=prediction
    ```
    + Through this, you will use `finetuned_model` which is your model to predict the testset. In `prediction/predictions.json`, the prediction result will be saved with `arxiv_id: prediction` format.

## Pretraining Masked Lanuage Modeling
This is removed, since training the generation model itself is enromous. Please focus on training the generation model.