<!--- SPDX-License-Identifier: Apache-2.0 -->

# BERT-Squad

## Use cases
This model answers questions based on the context of the given input paragraph.

## Description
BERT (Bidirectional Encoder Representations from Transformers) applies Transformers, a popular attention model, to language modelling. This mechanism has an encoder to read the input text and a decoder that produces a prediction for the task. This model uses the technique of masking out some of the words in the input and then condition each word bidirectionally to predict the masked words. BERT also learns to model relationships between sentences, predicts if the sentences are connected or not.

## Model

 |Model        |Download  |Download (with sample test data)| ONNX version |Opset version| Accuracy|
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
|BERT-Squad| [416 MB](model/bertsquad-8.onnx) |  [385 MB](model/bertsquad-8.tar.gz) |  1.3 | 8| |
|BERT-Squad| [416 MB](model/bertsquad-10.onnx) |  [384 MB](model/bertsquad-10.tar.gz) |  1.5 | 10| |
|BERT-Squad| [416 MB](model/bertsquad-12.onnx) |  [384 MB](model/bertsquad-12.tar.gz) |  1.9 | 12| 80.67171|
|BERT-Squad-int8| [119 MB](model/bertsquad-12-int8.onnx) |  [101 MB](model/bertsquad-12-int8.tar.gz) |  1.9 | 12| 80.43519|
> Compared with the fp32 BERT-Squad, BERT-Squad-int8's accuracy drop ratio is 0.29%, performance improvement is 1.81x.
>
> Note the performance depends on the test hardware. 
> 
> Performance data here is collected with Intel® Xeon® Platinum 8280 Processor, 1s 4c per instance, CentOS Linux 8.3, data batch size is 1.

Dependencies
* [tokenization.py](dependencies/tokenization.py)
* [run_onnx_squad.py](dependencies/run_onnx_squad.py)

## Inference
We used [ONNX Runtime](https://github.com/microsoft/onnxruntime) to perform the inference.

### Input
The input is a paragraph and questions relating to that paragraph. The model uses the WordPiece tokenization method to split the input paragraph and questions into list of tokens that are available in the vocabulary (30,522 words).
Then converts these tokens into features
<li>input_ids: list of numerical ids for the tokenized text
<li>input_mask: will be set to 1 for real tokens and 0 for the padding tokens
<li>segment_ids: for our case, this will be set to the list of ones
<li>label_ids: one-hot encoded labels for the text

### Preprocessing
Write an inputs.json file that includes the context paragraph and questions.
```python
%%writefile inputs.json
{
  "version": "1.4",
  "data": [
    {
      "paragraphs": [
        {
          "context": "In its early years, the new convention center failed to meet attendance and revenue expectations.[12] By 2002, many Silicon Valley businesses were choosing the much larger Moscone Center in San Francisco over the San Jose Convention Center due to the latter's limited space. A ballot measure to finance an expansion via a hotel tax failed to reach the required two-thirds majority to pass. In June 2005, Team San Jose built the South Hall, a $6.77 million, blue and white tent, adding 80,000 square feet (7,400 m2) of exhibit space",
          "qas": [
            {
              "question": "where is the businesses choosing to go?",
              "id": "1"
            },
            {
              "question": "how may votes did the ballot measure need?",
              "id": "2"
            },
            {
              "question": "By what year many Silicon Valley businesses were choosing the Moscone Center?",
              "id": "3"
            }
          ]
        }
      ],
      "title": "Conference Center"
    }
  ]
}
```
Get parameters and convert input examples into features
```python
# preprocess input
predict_file = 'inputs.json'

# Use read_squad_examples method from run_onnx_squad to read the input file
eval_examples = read_squad_examples(input_file=predict_file)

max_seq_length = 256
doc_stride = 128
max_query_length = 64
batch_size = 1
n_best_size = 20
max_answer_length = 30

vocab_file = os.path.join('uncased_L-12_H-768_A-12', 'vocab.txt')
tokenizer = tokenization.FullTokenizer(vocab_file=vocab_file, do_lower_case=True)

# Use convert_examples_to_features method from run_onnx_squad to get parameters from the input
input_ids, input_mask, segment_ids, extra_data = convert_examples_to_features(eval_examples, tokenizer,
                                                                              max_seq_length, doc_stride, max_query_length)
```

### Output
For each question about the context paragraph, the model predicts a start and an end token from the paragraph that most likely answers the questions.

### Postprocessing
Write the predictions (answers to the questions) in a file.
```python
# postprocess results
output_dir = 'predictions'
os.makedirs(output_dir, exist_ok=True)
output_prediction_file = os.path.join(output_dir, "predictions.json")
output_nbest_file = os.path.join(output_dir, "nbest_predictions.json")
write_predictions(eval_examples, extra_data, all_results,
                  n_best_size, max_answer_length,
                  True, output_prediction_file, output_nbest_file)
```

## Dataset (Train and Validation)
The model is trained with [SQuAD v1.1](https://rajpurkar.github.io/SQuAD-explorer/explore/1.1/dev/) dataset that contains 100,000+ question-answer pairs on 500+ articles.

## Validation accuracy
Metric is Exact Matching (EM) of 80.7, computed over SQuAD v1.1 dev data, for this onnx model.

## Training
Fine-tuned the model using SQuAD-1.1 dataset. Look at [BertTutorial.ipynb](https://github.com/onnx/tensorflow-onnx/blob/master/tutorials/BertTutorial.ipynb) for more information for converting the model from tensorflow to onnx and for fine-tuning

## Quantization
BERT-Squad-int8 is obtained by quantizing BERT-Squad model (opset=12). We use [Intel® Neural Compressor](https://github.com/intel/neural-compressor) with onnxruntime backend to perform quantization. View the [instructions](https://github.com/intel/neural-compressor/blob/master/examples/onnxrt/language_translation/onnx_model_zoo/bert-squad/quantization/ptq/readme.md) to understand how to use Intel® Neural Compressor for quantization.

### Environment
onnx: 1.9.0 
onnxruntime: 1.8.0

### Prepare model
```shell
wget https://github.com/onnx/models/raw/main/text/machine_comprehension/bert-squad/model/bertsquad-12.onnx
```

### Model quantize
```bash
bash run_tuning.sh --input_model=/path/to/model \ # model path as *.onnx
                   --output_model=/path/to/model_tune \
                   --dataset_location=/path/to/SQuAD/dataset \
                   --config=bert.yaml
```

## References
* **BERT** Model from the paper [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805)

* [BERT Tutorial](https://github.com/onnx/tensorflow-onnx/blob/master/tutorials/BertTutorial.ipynb)

* [Intel® Neural Compressor](https://github.com/intel/neural-compressor)

## Contributors
* [Kundana Pillari](https://github.com/kundanapillari)
* [mengniwang95](https://github.com/mengniwang95) (Intel)
* [airMeng](https://github.com/airMeng) (Intel)
* [ftian1](https://github.com/ftian1) (Intel)
* [hshen14](https://github.com/hshen14) (Intel)

## License
Apache 2.0
