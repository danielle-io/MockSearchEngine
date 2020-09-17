from collections import defaultdict
import json
import os

from createIndex import CreateIndex

class WebCrawler:

    fileName_to_URL = defaultdict(str)
    counter = 0
    url_counter = 0
    createIndex = CreateIndex()
    urls_with_nums = dict()
    corpusSize = 0

    def read_from_main_dir(self, mainDir):

        # This builds a dictionary of the URLS from bookkeeping.json so we can
        # access the url name with the folder number
        with open(mainDir + '/filePaths.json', 'r') as json_file:
            self.fileName_to_URL = json.load(json_file)
            self.corpusSize = len(self.fileName_to_URL)

        # loop over each dir in the main dir
        for singleSubDirName in os.scandir(mainDir):
            if singleSubDirName.is_dir():

                #for printing purposes
                self.counter += 1

                # singleSubDirName.path gets the name of the folder path
                # so instead of "3" its users/documents/maindir/3
                # get an array of all the files in our new directory
                self.loop_over_each_file_in_folder(singleSubDirName.name, singleSubDirName.path, os.scandir(singleSubDirName.path))

        self.createIndex.bulkInsert('main')
        self.createIndex.contentBulkInsert('main')

        self.createIndex.bulkInsert('twogram')
        self.createIndex.contentBulkInsert('twogram')


    def loop_over_each_file_in_folder(self, singleSubDirName: str, fullPathOfSubDir: str, fileList: list):


        for fileName in fileList:

            folderAndFileName = singleSubDirName + '/' + fileName.name
            urlName = self.fileName_to_URL[folderAndFileName]
            
            self.url_counter += 1

            # send the file name and the filepath to process lines so all LINES IN FILE can be processed
            self.createIndex.process_lines_in_files(urlName, fullPathOfSubDir, fileName.name, self.url_counter, self.corpusSize)

