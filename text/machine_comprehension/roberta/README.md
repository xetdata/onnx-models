<!--- SPDX-License-Identifier: Apache-2.0 -->

# RoBERTa

## Use cases
Transformer-based language model for text generation.

## Description
RoBERTa builds on BERT’s language masking strategy and modifies key hyperparameters in BERT, including removing BERT’s next-sentence pretraining objective, and training with much larger mini-batches and learning rates. RoBERTa was also trained on an order of magnitude more data than BERT, for a longer amount of time. This allows RoBERTa representations to generalize even better to downstream tasks compared to BERT.

## Model

 |Model        |Download  |Download (with sample test data)| ONNX version |Opset version|Accuracy|
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
|RoBERTa-BASE| [499 MB](model/roberta-base-11.onnx) |  [295 MB](model/roberta-base-11.tar.gz) |  1.6 | 11| 88.5|
|RoBERTa-SequenceClassification| [499 MB](model/roberta-sequence-classification-9.onnx) |  [432 MB](model/roberta-sequence-classification-9.tar.gz) |  1.6 | 9| MCC of [0.85](dependencies/roberta-sequence-classification-validation.ipynb)|

## Source
PyTorch RoBERTa => ONNX RoBERTa
PyTorch RoBERTa + script changes => ONNX RoBERTa-SequenceClassification

## Conversion
Here is the [benchmark script](https://github.com/microsoft/onnxruntime/blob/master/onnxruntime/python/tools/transformers/run_benchmark.sh) that was used for exporting RoBERTa-BASE model.

Tutorial for conversion of RoBERTa-SequenceClassification model can be found in the [conversion](https://github.com/SeldonIO/seldon-models/blob/master/pytorch/moviesentiment_roberta/pytorch-roberta-onnx.ipynb) notebook.

Official tool from HuggingFace that can be used to convert transformers models to ONNX can be found [here](https://github.com/huggingface/transformers/blob/master/src/transformers/convert_graph_to_onnx.py)

## Inference
We used [ONNX Runtime](https://github.com/microsoft/onnxruntime) to perform the inference.

Tutorial for running inference for RoBERTa-SequenceClassification model using onnxruntime can be found in the [inference](dependencies/roberta-inference.ipynb) notebook.

### Input
input_ids: Indices of input tokens in the vocabulary. It's a int64 tensor of dynamic shape (batch_size, sequence_length). Text tokenized by RobertaTokenizer.

For RoBERTa-BASE model:
Input is a sequence of words as a string. Example: "Text to encode: Hello, World"

For RoBERTa-SequenceClassification model:
Input is a sequence of words as a string including sentiment. Example: "This film is so good"


### Preprocessing
For RoBERTa-BASE and RoBERTa-SequenceClassification model use tokenizer.encode() to encode the input text:
```python
import torch
import numpy as np
from simpletransformers.model import TransformerModel
from transformers import RobertaForSequenceClassification, RobertaTokenizer

text = "This film is so good"
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
input_ids = torch.tensor(tokenizer.encode(text, add_special_tokens=True)).unsqueeze(0)  # Batch size 1
```

### Output
For RoBERTa-BASE model:
Output of this model is a float32 tensors ```[batch_size,seq_len,768]``` and ```[batch_size,768]```

For RoBERTa-SequenceClassification model:
Output of this model is a float32 tensor ```[batch_size, 2]```

### Postprocessing
For RoBERTa-BASE model:
```
last_hidden_states = ort_out[0]
```

For RoBERTa-SequenceClassification model:
Print sentiment prediction
```python
pred = np.argmax(ort_out)
if(pred == 0):
    print("Prediction: negative")
elif(pred == 1):
    print("Prediction: positive")
```

## Dataset
RoBERTa-BASE model was trained on five datasets:
* [BookCorpus](https://yknzhu.wixsite.com/mbweb), a dataset consisting of 11,038 unpublished books;
* [English Wikipedia](https://en.wikipedia.org/wiki/English_Wikipedia) (excluding lists, tables and headers) ;
* [CC-News](https://commoncrawl.org/2016/10/news-dataset-available/), a dataset containing 63 millions English news articles crawled between September 2016 and February 2019.
* [OpenWebText](https://github.com/jcpeterson/openwebtext), an opensource recreation of the WebText dataset used to train GPT-2,
* [Stories](https://arxiv.org/abs/1806.02847) a dataset containing a subset of CommonCrawl data filtered to match the story-like style of Winograd schemas.

Pretrained RoBERTa-BASE model weights can be downloaded [here](https://s3.amazonaws.com/models.huggingface.co/bert/roberta-base-pytorch_model.bin).

RoBERTa-SequenceClassification model weights can be downloaded [here](https://storage.googleapis.com/seldon-models/pytorch/moviesentiment_roberta/pytorch_model.bin).

## Validation accuracy
[GLUE (Wang et al., 2019)](https://gluebenchmark.com/) (dev set, single model, single-task finetuning)
 |Model        |MNLI |QNLI| QQP |RTE|SST-2|MRPC|CoLA|STS-B|
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
|```roberta.base```| 87.6 | 92.8 |  91.9 | 78.7|94.8|90.2|63.6|91.2|

Metric and benchmarking details are provided by [fairseq](https://github.com/pytorch/fairseq/tree/master/examples/roberta).

## Publication/Attribution
* [RoBERTa: A Robustly Optimized BERT Pretraining Approach](https://arxiv.org/pdf/1907.11692.pdf).Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Mandar Joshi, Danqi Chen, Omer Levy, Mike Lewis, Luke Zettlemoyer, Veselin Stoyanov

## References
* The RoBERTa-SequenceClassification model is converted directly from [seldon-models/pytorch](https://github.com/SeldonIO/seldon-models/blob/master/pytorch/moviesentiment_roberta/pytorch-roberta-onnx.ipynb)
* [Accelerate your NLP pipelines using Hugging Face Transformers and ONNX Runtime](https://medium.com/microsoftazure/accelerate-your-nlp-pipelines-using-hugging-face-transformers-and-onnx-runtime-2443578f4333)

## Contributors
[Kundana Pillari](https://github.com/kundanapillari)

## License
Apache 2.0
