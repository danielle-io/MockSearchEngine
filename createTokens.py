import os
from nltk import WordNetLemmatizer
from lxml import html
import re
import math
import sys
from bs4 import BeautifulSoup as Soup
import warnings


class CreateTokens:

    # treats warnings as errors so we can catch them using bs4
    warnings.simplefilter('error', UserWarning)

    # nltk.download('wordnet')
    lemmatizer = WordNetLemmatizer()

    # 173 stop words
    stop_words = {'on', "let's", 'so', "that's", 'below', 'the', 'is',
                  'which', 'their', 'after', 'an', 'her', 'before', 'how',
                  "he'll", 'if', "i'm", 'between', 'could', 'does', 'it',
                  'while', 'than', 'whom', 'my', 'further', "weren't",
                  'here', "she'd", 'his', 'there', 'with', "we've", 'cannot',
                  'but', 'up', 'had', "wouldn't", 'its', 'for', 'are', 'or',
                  'as', 'into', 'from', 'again', "when's", "wasn't", 'ought',
                  "won't", "shan't", 'until', 'herself', 'through', "he's",
                  "i'll", 'myself', "she's", 'in', 'once', "hadn't", 'only',
                  'did', 'they', 'being', "can't", "what's", 'very', 'would',
                  "haven't", "doesn't", "there's", "they've", 'do', "it's",
                  "they'll", 'am', "you'd", 'a', 'have', 'yourself', 'off',
                  "you're", 'were', "why's", 'hers', 'out', 'above', "he'd",
                  'i', 'was', 'each', 'yours', 'those', 'doing', 'you', 'who',
                  'more', 'she', "where's", 'some', "you'll", "we're", "couldn't",
                  "we'll", "aren't", 'under', "mustn't", 'to', 'most', "who's",
                  "we'd", 'no', "they'd", 'he', 'him', 'both', 'of', 'because',
                  "i'd", 'this', 'all', 'and', 'himself', 'yourselves', 'itself',
                  'over', 'why', 'these', 'any', "shouldn't", "didn't", 'having',
                  'not', 'our', 'own', 'at', 'should', 'themselves', "she'll",
                  'theirs', 'me', "isn't", 'same', 'by', 'been', 'such', 'them',
                  "i've", 'what', 'when', "here's", 'nor', 'other', 'too', 'be',
                  "don't", 'ours', 'ourselves', 'that', "you've", 'we', 'where',
                  "how's", 'during', 'has', 'down', 'then', "they're", 'few',
                  'against', "hasn't", 'your', 'about'}

    def create_markup_dict(self, markupDict: dict, line: str):
        # i, u, h5, h6 = 0.5
        # h2, h3, h4, bold, strong = 1
        # h1 = 2
        # title = 3
        try:
            soup = Soup(line, "html.parser")
            for section in soup.find_all(['h5', 'h6', 'i', 'u']):
                for word in self.getValidWords(section.text):
                    if word in markupDict.keys():
                        markupDict[word] += 0.5
                    else:
                        markupDict[word] = 0.5
            for section in soup.find_all(['h2', 'h3', 'h4', 'bold', 'strong', 'a']):
                for word in self.getValidWords(section.text):
                    if word in markupDict.keys():
                        markupDict[word] += 1
                    else:
                        markupDict[word] = 1
            for section in soup.find_all('h1'):
                for word in self.getValidWords(section.text):
                    if word in markupDict.keys():
                        markupDict[word] += 2
                    else:
                        markupDict[word] = 2
            for section in soup.find_all('title'):
                for word in self.getValidWords(section.text):
                    if word in markupDict.keys():
                        markupDict[word] += 3
                    else:
                        markupDict[word] = 3
        except UserWarning:
            pass


    def tokenize_words_in_line(self, snippetArr, urlsAndContentDict: dict, indexDictionary: dict,
                               helperArrayPositionDict: dict, line: str, urlName: str, markUpDict: dict, corpusSize):
        try:

            # remove html markup
            htmlParse = html.document_fromstring(line.encode("utf-8"))
            content = htmlParse.text_content()

            content = content.strip()
            content = content.lower()

            # Split words by space and punctuation
            for word in re.split('! |!|; |;|, |,|\s+|\.', content):

                if word not in self.stop_words:
                    word.replace('\'', '')
                    word.replace('\"', '')
                    word.replace('-', '')
                    word.replace('(', '')
                    word.replace(')', '')

                    # If its alphanumeric, but we allow # and $
                    if re.fullmatch(r"[#$a-zA-Z0-9]{2,}", word):

                        # Include this valid token in the returned snippet array
                        snippetArr.append(word)

                        # Example: removes s from plural words
                        wordAfterLemmatizer = self.lemmatizer.lemmatize(word)

                        if wordAfterLemmatizer:
                            # ADDED / IN FRONT OF $ TO NOT BREAK DATABASE
                            wordAfterLemmatizer = self.hideFirstCharDollarSign(wordAfterLemmatizer)

                            # Update content dictionary
                            if wordAfterLemmatizer in urlsAndContentDict[urlName]['words']:
                                urlsAndContentDict[urlName]['words'][wordAfterLemmatizer] += 1
                            else:
                                urlsAndContentDict[urlName]['words'][wordAfterLemmatizer] = 1


                        # if token is not yet in dictionary, insert it, with the value
                        # set to an empty dict.
                        position = -1

                        if wordAfterLemmatizer not in indexDictionary:

                            indexDictionary[wordAfterLemmatizer] = dict()
                            indexDictionary[wordAfterLemmatizer]['word'] = wordAfterLemmatizer
                            
                            # # INNER dict for the URL's keys (urlName and tf)
                            # indexDictionary[wordAfterLemmatizer]['urls'] = dict()
                            indexDictionary[wordAfterLemmatizer]['urls'] = []
                            indexDictionary[wordAfterLemmatizer]['urls'].append({
                                'urlName': urlName,
                                'tf': 1
                            })

                            # add the word to the arr index helper dict so we can know what
                            # INDEX the dictionary with the URL is at so we dont have to
                            # loop over it checking (cant index it in a list)
                            helperArrayPositionDict[wordAfterLemmatizer] = dict()
                            helperArrayPositionDict[wordAfterLemmatizer]['word'] = wordAfterLemmatizer

                            # we know its at index 0 since the URL list is empty in this if
                            helperArrayPositionDict[wordAfterLemmatizer]['urls'] = dict()
                            helperArrayPositionDict[wordAfterLemmatizer]['urls'][urlName] = 0

                        # token already in our index
                        else:


                            # check if URL is in the helper so we can get the array index number to alter the entry
                            if urlName in helperArrayPositionDict[wordAfterLemmatizer]['urls']:
                                position = helperArrayPositionDict[wordAfterLemmatizer]['urls'][urlName]

                                # update the dictionary at that position
                                indexDictionary[wordAfterLemmatizer]['urls'][position]['tf'] += 1

                                # url must be appended to the list, and that index must be added to the
                            # helper dictionary
                            else:
                                indexDictionary[wordAfterLemmatizer]['urls'].append({
                                    'urlName': urlName,
                                    'tf': 1
                                })

                                position = len(indexDictionary[wordAfterLemmatizer]['urls']) - 1
                                helperArrayPositionDict[wordAfterLemmatizer]['urls'][urlName] = position

                        lengthOfUrlDictionary = len(indexDictionary[wordAfterLemmatizer]['urls'])

                        indexDictionary[wordAfterLemmatizer]['df'] = lengthOfUrlDictionary

                        # Calculate the tfidf for every search
                        tf = indexDictionary[wordAfterLemmatizer]['urls'][position]['tf']

                        tfidf = self.getTfidf(int(tf), int(lengthOfUrlDictionary), corpusSize)

                        indexDictionary[wordAfterLemmatizer]['urls'][position]['tfidf'] = math.log(tfidf)

            # IF THE WORD IS IN SPECIAL MARKUP: add the tf that was in the already scanned markUpDict
            for word, additionalTf in markUpDict.items():
                if word in urlsAndContentDict[urlName]['words']:
                    urlsAndContentDict[urlName]['words'][word] += additionalTf

        except Exception as e:
            if str(e) != 'Document is empty':
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                # exit()

        # send back the line so that a snippet can be stored

        return snippetArr

    def twograms_tokenize_words_in_line(self, twogramUrlsAndContentDict: dict, twogramIndexDictionary: dict,
                                        twogramHelperArrayPositionDict: dict, line: str, urlName: str,
                                        markUpDict: dict, corpusSize):
        try:

            # remove html markup
            htmlParse = html.document_fromstring(line.encode("utf-8"))

            content = htmlParse.text_content()

            content = content.strip()
            content = content.lower()

            # Split words by. ......
            all_words = re.split('; |;|, |,|\s+|\.', content)
            count = 0

            while count < len(all_words):

                if count + 1 <= len(all_words) - 1:
                    word = all_words[count]
                    second_word = all_words[count + 1]

                    if word not in self.stop_words and second_word not in self.stop_words:
                        word.replace('\'', '')
                        word.replace('\"', '')
                        word.replace('-', '')
                        word.replace('(', '')
                        word.replace(')', '')

                        second_word.replace('\'', '')
                        second_word.replace('\"', '')
                        second_word.replace('-', '')
                        second_word.replace('(', '')
                        second_word.replace(')', '')

                        if re.fullmatch(r"[#$a-zA-Z0-9]{2,}", word) and re.fullmatch(r"[#$a-zA-Z0-9]{2,}", second_word):  # consider

                            wordAfterLemmatizer = self.lemmatizer.lemmatize(word)

                            secondWordAfterLemmatizer = self.lemmatizer.lemmatize(second_word)

                            wordAfterLemmatizer += ' ' + secondWordAfterLemmatizer


                            # ADDED / IN FRONT OF $ TO NOT BREAK DATABASE
                            if wordAfterLemmatizer:
                                wordAfterLemmatizer = self.hideFirstCharDollarSign(wordAfterLemmatizer)

                                # IF THE WORD IS NOT IN SPECIAL MARKUP: add one or set to one for tf
                                if not wordAfterLemmatizer in markUpDict.keys():
                                    # Update content dictionary
                                    if wordAfterLemmatizer in twogramUrlsAndContentDict[urlName]['words']:
                                        twogramUrlsAndContentDict[urlName]['words'][wordAfterLemmatizer] += 1

                                    else:
                                        twogramUrlsAndContentDict[urlName]['words'][wordAfterLemmatizer] = 1

                                # IF THE WORD IS IN SPECIAL MARKUP: add the tf that was in the alreadu scanned markUpDict
                                else:
                                    # Update content dictionary
                                    if wordAfterLemmatizer in twogramUrlsAndContentDict[urlName]['words']:
                                        twogramUrlsAndContentDict[urlName]['words'][wordAfterLemmatizer] += markUpDict[
                                            wordAfterLemmatizer]


                                    else:
                                        twogramUrlsAndContentDict[urlName]['words'][wordAfterLemmatizer] = markUpDict[
                                            wordAfterLemmatizer]

                            # if token is not yet in dictionary, insert it, with the value
                            # set to an empty dict.
                            position = -1

                            if wordAfterLemmatizer not in twogramIndexDictionary:

                                twogramIndexDictionary[wordAfterLemmatizer] = dict()
                                twogramIndexDictionary[wordAfterLemmatizer]['word'] = wordAfterLemmatizer

                                # add the word to the arr index helper dict so we can know what
                                # INDEX the dictionary with the URL is at so we dont have to
                                # loop over it checking (cant index it in a list)
                                twogramHelperArrayPositionDict[wordAfterLemmatizer] = dict()
                                twogramHelperArrayPositionDict[wordAfterLemmatizer]['word'] = wordAfterLemmatizer

                                # we know its at index 0 since the URL list is empty in this if
                                twogramHelperArrayPositionDict[wordAfterLemmatizer]['urls'] = dict()
                                twogramHelperArrayPositionDict[wordAfterLemmatizer]['urls'][urlName] = 0

                                # # INNER dict for the URL's keys (urlName and tf)
                                twogramIndexDictionary[wordAfterLemmatizer]['urls'] = []
                                twogramIndexDictionary[wordAfterLemmatizer]['urls'].append({
                                    'urlName': urlName,
                                    'tf': 1
                                })

                            # token already in our index
                            else:

                                # print(urlsAndContentDict)
                                # check if URL is in the helper so we can get the array index number to alter the entry
                                if urlName in twogramHelperArrayPositionDict[wordAfterLemmatizer]['urls']:
                                    position = twogramHelperArrayPositionDict[wordAfterLemmatizer]['urls'][urlName]

                                    # update the dictionary at that position
                                    twogramIndexDictionary[wordAfterLemmatizer]['urls'][position]['tf'] += 1

                                    # url must be appended to the list, and that index must be added to the
                                # helper dictionary
                                else:
                                    twogramIndexDictionary[wordAfterLemmatizer]['urls'].append({
                                        'urlName': urlName,
                                        'tf': 1
                                    })

                                    position = len(twogramIndexDictionary[wordAfterLemmatizer]['urls']) - 1
                                    twogramHelperArrayPositionDict[wordAfterLemmatizer]['urls'][urlName] = position

                            lengthOfUrlDictionary = len(twogramIndexDictionary[wordAfterLemmatizer]['urls'])
                            twogramIndexDictionary[wordAfterLemmatizer]['df'] = lengthOfUrlDictionary

                            # Calculate the tfidf for every search
                            tf = twogramIndexDictionary[wordAfterLemmatizer]['urls'][position]['tf']

                            tfidf = self.getTfidf(int(tf), int(lengthOfUrlDictionary), corpusSize)

                            twogramIndexDictionary[wordAfterLemmatizer]['urls'][position]['tfidf'] = tfidf

                count += 1

            # IF THE WORD IS IN SPECIAL MARKUP: add the tf that was in the already scanned markUpDict
            for word, additionalTf in markUpDict.items():
                if word in twogramUrlsAndContentDict[urlName]['words']:
                    twogramUrlsAndContentDict[urlName]['words'][word] += additionalTf

        except Exception as e:
            if str(e) != 'Document is empty':
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                # exit()


    def getTfidf(self, tf, df, totalDocs):
        return (1 + math.log(tf)) * math.log(totalDocs / df)

    def hideFirstCharDollarSign(self, stringToCheck):
        while stringToCheck[0] == '$':
            stringToCheck = '/' + stringToCheck
        return stringToCheck
    
    def getValidWords(self, content):
        validWords = []
        content = content.strip()
        content = content.lower()
        for word in re.split('! |!|; |;|, |,|\s+|\.', content):
            if word not in self.stop_words:
                word.replace('\'', '')
                word.replace('\"', '')
                word.replace('-', '')
                word.replace('(', '')
                word.replace(')', '')

                if re.fullmatch(r"[#$a-zA-Z0-9]{2,}", word):
                    wordAfterLemmatizer = self.lemmatizer.lemmatize(word)

                    # ADDED / IN FRONT OF $ TO NOT BREAK DATABASE
                    if wordAfterLemmatizer:
                        wordAfterLemmatizer = self.hideFirstCharDollarSign(wordAfterLemmatizer)

                    validWords.append(wordAfterLemmatizer)
        return validWords
        
