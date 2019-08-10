import json 
import malaya
from preprocess import *


# for the first time run this to download the stopwrods and pukt data
# nltk.download('stopwords')
# nltk.download('punkt')



print("Enter the offset of the twitt you would like to analayze :")
id = input()

with open("dataset.json", "r") as read_file:
    data = json.load(read_file)


# for i in range(0,2):
#     text = data['data'][int(i)]['text']
#     text = preprocess(text)
#     data['data'][int(id)]['text'] = ' '.join(text)

# with open('after.json', 'w') as outfile:
#     json.dump(data, outfile)

text = data['data'][int(id)]['text']
p = preprocess(text)
print("processed Sentence:",p)
searchforgif(' '.join(p),text)



