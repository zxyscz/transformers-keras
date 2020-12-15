import os
import json
import logging

import tensorflow as tf

from .abstract_adapter import AbstractAdapter
from .abstract_adapter import parse_pretrained_model_files


class BertAdapter(AbstractAdapter):
    """Adapte pretrained models to newly build BERT model."""

    def adapte(self, pretrained_model_dir, **kwargs):
        config_file, ckpt, vocab_file = parse_pretrained_model_files(pretrained_model_dir)
        model_config = self.adapte_config(config_file)
        variables_mapping = self.adapte_variables(model_config['num_layers'])
        return model_config, variables_mapping, ckpt, vocab_file 

    
    def adapte_config(self, config_file):
        with open(config_file, mode='rt', encoding='utf8') as fin:
            config = json.load(fin)

        model_config = {
            'vocab_size': config['vocab_size'],
            'activation': config['hidden_act'],
            'max_positions': config['max_position_embeddings'],
            'hidden_size': config['hidden_size'],
            'type_vocab_size': config['type_vocab_size'],
            'intermediate_size': config['intermediate_size'],
            'hidden_dropout_rate': config['hidden_dropout_prob'],
            'attention_dropout_rate': config['attention_probs_dropout_prob'],
            'stddev': config['initializer_range'],
            'num_layers': config['num_hidden_layers'],
            'num_attention_heads': config['num_attention_heads'],
        }
        return model_config

    def adapte_variables(self, num_layers=12):
        mapping = {}
        
        # embedding 
        mapping.update({
            'bert/embedding/weight:0': 'bert/embeddings/word_embeddings',
            'bert/embedding/token_type_embedding/embeddings:0': 'bert/embeddings/token_type_embeddings',
            'bert/embedding/position_embedding/embeddings:0': 'bert/embeddings/position_embeddings',
            'bert/embedding/layer_norm/gamma:0': 'bert/embeddings/LayerNorm/gamma',
            'bert/embedding/layer_norm/beta:0': 'bert/embeddings/LayerNorm/beta',
        })

        # encoder 
        model_prefix = 'bert/encoder/layer_{}'
        for i in range(num_layers):
            encoder_prefix = 'bert/encoder/layer_{}/'.format(i)
            # attention
            attention_prefix = encoder_prefix + 'attention/'
            for n in ['query', 'key', 'value']:
                for w in ['kernel', 'bias']:
                    mapping[attention_prefix + n + '/' + w + ':0'] = attention_prefix + 'self/' + n + '/' + w
            #
            mapping[attention_prefix + 'dense/kernel:0'] = attention_prefix + 'output/dense/kernel'
            mapping[attention_prefix + 'dense/bias:0'] = attention_prefix + 'output/dense/bias'
            mapping[attention_prefix + 'layer_norm/gamma:0'] = attention_prefix + 'output/LayerNorm/gamma'
            mapping[attention_prefix + 'layer_norm/beta:0'] = attention_prefix + 'output/LayerNorm/beta'
            # intermediate
            intermediate_prefix = encoder_prefix + 'intermediate/'
            mapping[intermediate_prefix + 'dense/kernel:0'] = intermediate_prefix + 'dense/kernel'
            mapping[intermediate_prefix + 'dense/bias:0'] = intermediate_prefix + 'dense/bias'
            # output
            mapping[encoder_prefix + 'dense/kernel:0'] = encoder_prefix + 'output/dense/kernel'
            mapping[encoder_prefix + 'dense/bias:0'] = encoder_prefix + 'output/dense/bias'
            mapping[encoder_prefix + 'layer_norm/gamma:0'] = encoder_prefix + 'output/LayerNorm/gamma'
            mapping[encoder_prefix + 'layer_norm/beta:0'] = encoder_prefix + 'output/LayerNorm/beta'

        # pooler
        mapping['bert/pooler/dense/kernel:0'] = 'bert/pooler/dense/kernel'
        mapping['bert/pooler/dense/bias:0'] = 'bert/pooler/dense/bias'

        return mapping
