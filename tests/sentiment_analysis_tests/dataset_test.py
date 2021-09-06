import unittest

from transformers_keras.sentiment_analysis.dataset import BertForAspectTermExtractionDataset


class DatasetTest(unittest.TestCase):
    """Dataset test"""

    def test_build_dataset(self):
        print("====from_jsonl_files\n")
        d = BertForAspectTermExtractionDataset.from_jsonl_files(
            "testdata/ate.jsonl", vocab_file="testdata/bert.vocab.txt", batch_size=2
        )
        print(next(iter(d)))

        print("====jsonl_to_examples\n")
        examples = BertForAspectTermExtractionDataset.jsonl_to_examples(
            "testdata/ate.jsonl", vocab_file="testdata/bert.vocab.txt"
        )
        for i in range(2):
            print(examples[i])

        print("====from_examples\n")
        d = BertForAspectTermExtractionDataset.from_examples(examples, batch_size=2)
        print(next(iter(d)))

        print("====examples_to_tfrecord\n")
        BertForAspectTermExtractionDataset.examples_to_tfrecord(examples, output_files=["testdata/ate.tfrecord"])

        print("====from_tfrecord_files\n")
        d = BertForAspectTermExtractionDataset.from_tfrecord_files(input_files=["testdata/ate.tfrecord"])
        print(next(iter(d)))


if __name__ == "__main__":
    unittest.main()
