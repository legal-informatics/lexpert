#!/usr/bin/env python
# coding: utf8
import pickle
import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
import re

# New entity labels
LABEL = ['I-loc', 'B-loc', 'I-date', 'B-date', 'B-deriv-per', 'I-per', 'B-per', 'I-org', 'B-org', "I-misc", "B-misc"]

"""
org = Organization
per = Person
loc = location
date = date
"""


# Loading training data
def fix(tup):
    return (tup[0].replace('""""', ""), tup[1])


def trim_entity_spans(data: list) -> list:
    """Removes leading and trailing white spaces from entity spans.

    Args:
        data (list): The data to be cleaned in spaCy JSON format.

    Returns:
        list: The cleaned data.
    """
    invalid_span_tokens = re.compile(r'\s')

    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            valid_start = start
            valid_end = end
            while valid_start < len(text) and invalid_span_tokens.match(
                text[valid_start]):
                valid_start += 1
            while valid_end > 1 and invalid_span_tokens.match(
                text[valid_end - 1]):
                valid_end -= 1
            valid_entities.append([valid_start, valid_end, label])
        cleaned_data.append([text, {'entities': valid_entities}])

    return cleaned_data


def main(path, model=None, new_model_name='new_model', output_dir=None, n_iter=10):
    """Setting up the pipeline and entity recognizer, and training the new entity."""
    with open(path, 'rb') as fp:
        train_data = pickle.load(fp)
    trim_entity_spans(train_data)
    train_data = [fix(el) for el in train_data]
    if model is not None:
        nlp = spacy.load(model)  # load existing spacy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('xx')  # create blank Language class
        print("Created blank 'xx' model")
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe('ner')

    # for i in LABEL:
    #    ner.add_label(i)  # Add new entity labels to entity recognizer

    for _, annotations in train_data:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.entity.create_optimizer()

    # Get names of other pipes to disable them during training to train only NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                texts = [str.strip(text) for text in texts]
                try:
                    nlp.update(texts, annotations, sgd=optimizer, drop=0.35, losses=losses)
                except Exception as e:
                    print(e)
            if losses['ner'] < 20:
                break
            print('Losses', losses)

    # Test the trained model
    test_text = 'Republika Srbija se odriće Kosova na dan 22. maja 2019. godine, i prestonica drzave je  u Novi Sad.'
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # Save model 
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # Test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == '__main__':
    main('../data/spacy/reldiD_spacy.json', None, "model", output_dir="../data/spacy/model2", n_iter=50)
