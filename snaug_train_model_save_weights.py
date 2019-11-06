"""
Train and save model data (tokens, weights, etc) to be used on different platforms
"""

from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical

import string
import textwrap
import pickle

from lib.nlplstm_class import (TFModelLSTMWordToken, TFModelLSTMWord2vec) 
from lib.data_common import (load_doc, save_doc, clean_doc)
from lib.data_common import (build_token_lines, prepare_text_tokens, load_word2vec)


# 
# Loading, saving and pre-processing of the text data source
#

pathfinder_textfile = './data/textgen_pathfinder.txt'
fixed_length_token_textfile = './data/pathfinder_fixed-length_tokens.txt'

# load document
docs = load_doc(pathfinder_textfile)
#print(docs[:200])
print(textwrap.fill('%s' % (docs[:200]), 80))

# pre-process and tokenize document
tokens = clean_doc(docs)
print(tokens[:20])
print('Total Tokens: %d' % len(tokens))
print('Unique Tokens: %d' % len(set(tokens)))

# organize into fixed-length lines of tokens
lines = build_token_lines(tokens, length=50)
print('Total lines: %d' % len(lines))

# save fixed-length lines to file
save_doc(lines, fixed_length_token_textfile)

# tokenize and separate into input and output
X, y, seq_length, vocab_size, tokenizer = prepare_text_tokens(lines)
print(X.shape)


#
# Word tokenization with word embedding model
#

# create new object that is an LSTM model using word tokenization
# and word embedding to generate text
textgen_model_2 = TFModelLSTMWordToken(use_gpu=False)
	
# sanity check
print(textgen_model_2.model_name)
print(textgen_model_2.have_gpu)
print(textgen_model_2.use_cudadnn)

# define and compile the model parameters
textgen_model_2.define(vocab_size=vocab_size, 
                       embedding_size=100, 
                       seq_length=seq_length)
print(textgen_model_2.model.summary())

# compile model
textgen_model_2.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# fit model
#history = textgen_model_2.fit(X, y, batch_size=128, epochs=200)
history = textgen_model_2.fit(X, y, batch_size=128, epochs=2)

# serialize model weights to HDF5 and save model training history
textgen_model_2.save_trained_model_data(fname_prefix="./model/pathfinder_wordtoken_model_200_epoch")

print()

#
# Word2vec pre-trained model
#

# get pretrained weights for LSTM model's word embedding using Gensim Word2vec
vocab_size, emdedding_size, pretrained_weights = load_word2vec(lines)

# save gensim Word2Vec word model's pretrained weights
pickle.dump(pretrained_weights, open('./model/pathfinder_wordtoken_w2v_word_model_weights.pkl', 'wb'))

# create new object that is an LSTM model using word tokenization
# and pre-trained Word2vec model from Gensim to generate text
textgen_model_3 = TFModelLSTMWord2vec(use_gpu=False)

print(textgen_model_3.model_name)
print(textgen_model_3.have_gpu)
print(textgen_model_3.use_cudadnn)

textgen_model_3.define(vocab_size=vocab_size, 
                             embedding_size=emdedding_size, 
                             pretrained_weights=pretrained_weights)
print(textgen_model_3.model.summary())

# compile model
textgen_model_3.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# fit model
#history = model.fit(X, y, batch_size=128, epochs=100)
#history = textgen_model_3.fit(X, y, batch_size=128, epochs=50)
history = textgen_model_3.fit(X, y, batch_size=128, epochs=2)

# serialize model weights to HDF5 and save model training history
textgen_model_3.save_trained_model_data(fname_prefix="./model/pathfinder_wordtoken_w2v_model_50_epoch")
