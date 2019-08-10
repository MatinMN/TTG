import re, string, unicodedata
import nltk
import contractions
import inflect
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
from lxml import html
import requests
import malaya
from dialex import dialex
import urllib,json
from tkinter import *
from PIL import Image,ImageTk
import io
import pyglet
import time
from googletrans import Translator
from abbr import *
from gtrans import translate_text, translate_html

def replace_contractions(text):
    """Replace contractions in string of text"""
    return contractions.fix(text)

def remove_tags(sample):
    """Remove tags from a sample string"""
    return re.sub('<[^<]+?>',"", sample)

def remove_URL(sample):
    """Remove URLs from a sample string"""
    return re.sub(r"(?:\@|https?\://)\S+", "", sample)

def fixabbriviation(sample,lang):
    api = dialex.Dialex('jeJEWS2IPIgsCCYcwhbgiUhe0Eter4gYWwk')
    sample = api.transform(sample, lang)
    # print(sample)
    return sample

def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words

def fixabbrfromdata(words):
    """Stem words in list of tokenized words"""
    new_words = []
    for word in words:
         if word in abbrlist:
             new_words.append(abbrlist[word])
         else:     
            new_words.append(word)
    return new_words

def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = LancasterStemmer()
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems

def lemmatize_verbs(words):
    """Lemmatize verbs in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas

def normalize(words):
    words = remove_non_ascii(words)
    words = fixabbrfromdata(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words)
    return words

def normalize_ml(words):
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words)
    return words

def interjectionfind(text):
    inter=['Hmmm','?','hmm', 'hmmm', 'ahem', 'aah', 'ooh', 'boo', 'eh', 'eww', 'ewww', 'jeez', 'ooh la la', 'ooh-la-la', 'ohh la-la', 'oops', 'phew', 'whoa', 'yoo hoo', 'yahoo', 'yeah','grr', 'grrr', 'duh', 'bah', 'ow', 'shh', 'uh-huh', 'yuck', 'pow', 'hush', 'voila', 'pfft']
    il=[]

    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.split()

    for w in text:
        if w in inter:
            il.append(w)
            
    return ' '.join(il)


def spellcorrectionmalay(words):
    malays = malaya.load_malay_dictionary()
    corrector = malaya.spell.fuzzy(malays)
    """ correct spelling of malay words"""
    corrected = []
    for word in words:
        correct = corrector.correct(word,debug=False,fast = False,assume_wrong = True)
        corrected.append(correct)
    return corrected

def preprocess(sample):
    multinomial = malaya.language_detection.multinomial()

    malays = malaya.load_malay_dictionary()
    # corrector = malaya.spell.fuzzy(malays)
    corrector = malaya.spell.probability()

    preprocessing = malaya.preprocessing.preprocessing(speller = corrector,translate_english_to_bm = False,expand_hashtags = False)
    
    #detect langauge
    lang = multinomial.predict(sample)
    # Normalize
    sample = remove_URL(sample)
    sample = replace_contractions(sample)
    interjections = interjectionfind(sample)
    if(len(interjections) > 1):
        sample = interjections
        return nltk.word_tokenize(sample)
    translator = Translator()
    if lang == 'ENGLISH':
        print("Language : " + lang)
        sample = fixabbriviation(sample,'en')
        # Tokenize
        words = nltk.word_tokenize(sample)
        
        return normalize(words)

    elif(lang == 'MALAY'): 
        print("Language : " + lang)
        sample = fixabbriviation(sample,'ms')
        res = preprocessing.process(sample)
        res = fixabbrfromdata(res)
        res = remove_tags(' '.join(res))
        print("Translating ...")
        # translated_text = translator.translate(res, src='ms',dest='en').text
        return nltk.word_tokenize(res)
    else:
        print("Wasn't able to detect the language")

        sample = fixabbriviation(sample,'ms')
        res = preprocessing.process(sample)
        res = fixabbrfromdata(res)
        res = remove_tags(' '.join(res))
        print("Translating ...")
        # translated_text = translator.translate(res, src='ms',dest='en').text
        return nltk.word_tokenize(res)

def searchforgif(text,original):
    api_key = "KVsNFGOZyR6GXwFLeeDYQIufdjN85WjC"
    if(len(text) <1):
        text = 'nothing'
        print("Unable to find a good search key word")
    if(text == '?' or text == '? ?'):
        text = "question"

    print(text)
    text = urllib.parse.quote(text)

    print("getting Gifs .... please wait")

    res = requests.get("http://api.giphy.com/v1/gifs/search?q="+text+"&api_key="+api_key+"&limit=7")
    data = json.loads(res.content)
    
    # print(data)

    print("Displaying the gifs")
    
    window = pyglet.window.Window(1400,200)
    label = None

    gifs = []
    for i in range(0,7):
        print("Getting Gif " + str(i))

        url = data['data'][i]['images']['fixed_width']['url']
        width = data['data'][i]['images']['fixed_width']['width']
        urllib.request.urlretrieve(url, str(i)+'.gif')
        time.sleep(.5)
        animation = pyglet.resource.animation(str(i)+'.gif')
        gif = pyglet.sprite.Sprite(animation,x=i*int(width))
        gifs.append(gif)

        print("Gif url : " + url)
            

    @window.event
    def on_draw():
        window.clear()
        for i in range(0,7):
            gifs[i].draw()
            
        window.flip()
    time.sleep(1)
    pyglet.app.run()    
    # mainWindow.mainloop()