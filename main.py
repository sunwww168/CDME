#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import CDME
import datetime


if __name__ == '__main__':

    # "Input: a dataset name "

    #fnamelist =['football']
    fnamelist = ["karate", "dolphins", 'football', 'polbooks']

    for fname in fnamelist:

        dirpath = './'

        if os.path.isdir(dirpath):

            "Set a output folder"
            outdirpath = dirpath + "/output"
            if not os.path.isdir(outdirpath):
                os.mkdir(outdirpath)           
            datafile = dirpath+"/dataset/"+fname+'.dat'
            if os.path.isfile(datafile):
                "Set up the graph list"               
                cur_graph = CDME.non_overlap_cdme(datafile, fname)                
                print ("start:")
                starttime = datetime.datetime.now()
                #community detection by CDME
                cur_graph.community_detection_cdme(outdirpath, fname)
               
                endtime = datetime.datetime.now()
                time_cost = (endtime - starttime).seconds
                print ("runtime:" + str(time_cost) + " s")
                #output the result 
                f = open(outdirpath + "/" + fname + ".txt", "a")                

                f.write("\n\n\n\n")
                f.write("runtime:  \n")
                f.write(str(time_cost)+" s")
                f.write("\n\n\n\n")
                f.close()
                print ("Done!")
                print ("\n\n\n\n")
                '''
                    TODO:
                    Do some analysis and plot 
                '''
            else:
                print("The dataset is not a directory!")

        else:
            print("The input is not a directory!")