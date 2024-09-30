import numpy as np
from keras.models import Sequential
from keras.layers import Embedding, Dropout, Conv1D, GlobalMaxPooling1D, Dense
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping
from keras.utils import plot_model
import pickle

# convolutional neural network (CNN) architecture

vocab_size = 5000
maximum_sequence_length = 500
embedding_dim = 16  

def start_model(filtered_reviews, all_sentiments):
    all_sentiments = all_sentiments.split()
    tokenizer = Tokenizer(num_words=vocab_size)
    tokenizer.fit_on_texts(filtered_reviews)
    tokenized_reviews = tokenizer.texts_to_sequences(filtered_reviews)
    X = pad_sequences(tokenized_reviews, padding='post', maxlen=maximum_sequence_length)
    y = np.array([0 if label == 'negative' else 1 for label in all_sentiments])
    X_train, X_val_test, y_train, y_val_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_val_test, y_val_test, test_size=0.5, random_state=42)

    model = Sequential()
    # strat embedding - pe scurt, e folosit pentru a converti un cuvant intr-un vector format din numere reale de lungime fixa
    model.add(Embedding(input_dim=5000, output_dim=16, input_length=500))
    # strat convolutional, folosit pentru a agrega valori asemanatoare. 
    model.add(Conv1D(filters = 128, kernel_size= 5, activation='relu'))
    # mai departe, stratul globalmaxpooling va reduce dimensiunea output-ului stratului conv1d. astfel, featurile cele mai importante vor ramane.
    model.add(GlobalMaxPooling1D())
    # mai departe, se va folosi un strat dense, in care fiecare neuron din el va avea ca input rezultatul tuturor neuronilor din stratul precedent. mai departe, se va aplica o transformare neliniara asupra a ceea ce contine fiecare neuron pentru a scapa de liniaritate si overfitting.
    model.add(Dense(128, activation='relu'))
    # se aplica ca neuronii sa mentina capacitatea de a prezice input necunoscut
    model.add(Dropout(0.5))
    # folosit in cazul de fata pentru a clasifica inputul cu 0 sau 1.
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_val, y_val), 
                    callbacks=[EarlyStopping(patience=3)])

    plot_model(model, to_file='model_architecture.png', show_shapes=True, show_layer_names=True)

    model.save('trained_imdb.h5')
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f'Test loss: {loss}, Test accuracy: {accuracy}')


def load_tokenizer(filename):
    with open(filename, 'rb') as handle:
        tokenizer = pickle.load(handle)
    return tokenizer