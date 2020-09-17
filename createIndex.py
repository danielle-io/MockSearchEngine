from mainDatabase import MainDatabase
import os
import sys

from createTokens import CreateTokens

class CreateIndex:

    file_path_list = []
    database = MainDatabase()

    # the main index dictionary & content dictionary
    indexDictionary = dict()
    urlsAndContentDict = dict()

    # the two gram index dictionary & content dictionary
    twogramIndexDictionary = dict()
    twogramUrlsAndContentDict = dict()


    helperArrayPositionDict = dict()
    twogramHelperArrayPositionDict = dict()


    def bulkInsert(self, dictName):
        currentDict = {}

        if (dictName == 'main'):
            currentDict = self.indexDictionary
        else:
            currentDict = self.twogramIndexDictionary

        count = 0
        docList = []
        lenTokens = len(currentDict)
        tokenAmount = 0
        for i in currentDict:
            if count == 10000:
                tokenAmount += 10000
                if (dictName == 'main'):
                    self.database.bulk_insert(docList)
                else:
                    self.database.twogram_bulk_insert(docList)

                print('Inserted ',tokenAmount, ' / ', lenTokens)

                count = 0
                docList = []
            docList.append(currentDict[i])
            count += 1

        # insert remaining docs
        if len(docList) != 0:
            self.database.bulk_insert(docList)


    def contentBulkInsert(self, dictName):
        currentDict = {}

        if (dictName == 'main'):
            currentDict = self.urlsAndContentDict
        else:
            currentDict = self.twogramUrlsAndContentDict

        count = 0
        docList = []
        lenTokens = len(currentDict)
        tokenAmount = 0

        for i in currentDict:
            if count == 10000:
                tokenAmount += 10000
                if (dictName == 'main'):
                    self.database.bulk_insert_content(docList)
                else:
                    self.database.twogram_bulk_insert_content(docList)

                print('CONTENT DICT Inserted ',tokenAmount, ' / ', lenTokens)

                count = 0
                docList = []
            docList.append(currentDict[i])
            count += 1

        # insert remaining docs
        if len(docList) != 0:
            if (dictName == 'main'):
                self.database.bulk_insert_content(docList)
            else:
                print('inserting into twogram_bulk_insert')
                self.database.twogram_bulk_insert_content(docList)

    def process_lines_in_files(self, urlName, filePath, fileName, url_counter, corpusSize):
        tokenizeContent = TokenizeContent()

        # Set up a dictionary for the content for each URL + the snippet
        self.urlsAndContentDict[urlName] = dict()
        self.urlsAndContentDict[urlName]['url'] = urlName
        self.urlsAndContentDict[urlName]['words'] = dict()
        self.urlsAndContentDict[urlName]['snippet'] = urlName

        # Set up a twol gram dictionary for the content for each URL + the snippet
        self.twogramUrlsAndContentDict[urlName] = dict()
        self.twogramUrlsAndContentDict[urlName]['url'] = urlName
        self.twogramUrlsAndContentDict[urlName]['words'] = dict()
        self.twogramUrlsAndContentDict[urlName]['snippet'] = urlName


        snippetArr = []

        # for the normal index
        for line in open(os.path.join(filePath, fileName), encoding="utf8"):

            markup_dict = dict()
            tokenizeContent.create_markup_dict(markup_dict, line)

            snippetArr = tokenizeContent.tokenize_words_in_line(snippetArr, self.urlsAndContentDict,
                                                                self.indexDictionary, self.helperArrayPositionDict,
                                                                line, urlName, url_counter, markup_dict, corpusSize)


            # now store the two grams as well
            tokenizeContent.twograms_tokenize_words_in_line(self.twogramUrlsAndContentDict,
                                                   self.twogramIndexDictionary, self.twogramHelperArrayPositionDict,
                                                   line, urlName, url_counter, markup_dict, corpusSize)


            try:
                if snippetArr:

                    # Store the first two lines as the snippet
                    if len(snippetArr) > 0 and len(snippetArr) < 30:
                        if len(snippetArr) >= 29:
                         snippetArr = snippetArr[15::]
                        earlyWords = ' '.join(snippetArr)
                        earlyWords = self.hideFirstCharDollarSign(earlyWords)

                        self.urlsAndContentDict[urlName]['snippet'] = earlyWords
                        self.twogramUrlsAndContentDict[urlName]['snippet'] = earlyWords


            except Exception as e:
                print('issues with join ', e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)



    def hideFirstCharDollarSign(self, stringToCheck):
        if stringToCheck[0] == '$':
            stringToCheck = '/' + stringToCheck
        return stringToCheck




