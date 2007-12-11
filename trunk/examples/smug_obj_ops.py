#!/bin/python

''' This example will return the URL of a random image from a users gallery'''
import smugmugapi.functional as SI
from smugmugapi.obj import *
import sys
import logging
import random
import urllib
import os
from optparse import OptionParser

def init_parser ():

    # python smug_func_ops.py -e EMAIL -p PASSWORD -m upload_image -a ALBUMID -f IMAGEPATH
    # python smug_func_ops.py -e EMAIL -p PASSWORD -m random_image -d
    # python smug_func_ops.py -e EMAIL -p PASSWORD -m get_albums -n NICK -d

    parser = OptionParser(usage="%prog -m MODE [-e EMAIL] [-p PASSWORD] [-d]")

    parser.add_option("-e", "--email",
                      action="store", type="string", dest="email",
                      help="XYZ")
    parser.add_option("-p", "--password",
                      action="store", type="string", dest="password",
                      help="XYZ")

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enable debugging [default: %default]")


    return parser


def main ():
    smugmug_api_key = "29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"  # API key

    parser = init_parser()
    (options, args) = parser.parse_args()

    # this is just a crude test. Actual examples will be added later (TBD)
    session = Session (SI.SmugMugAPI("29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"), options.email, options.password, options.debug)

    print "------------------------------------------------------------------------------------------------"
    album = Album.get (session=session, id=3914389)
    print album.Position
    import random
    album.Title = "dXYXYXYXYXYwYsd" + str (random.randint(1,1000000))
    album.save()
    print album.get_statistics (1,2007)


    print "------------------------------------------------------------------------------------------------"
    # Image tests #######################
    album = Album.get (session=session, id=3914389)
    print "Enter a key to view the category"
    raw_input()
    print album.category

    print "------------------------------------------------------------------------------------------------"
    image_list = Image.get_all (session=session, album=album)


    # Album tests #######################
    # get the test album
    print "------------------------------------------------------------------------------------------------"
    album = Album.get (session=session, id=3914389)
    print album.Position
    import random
    album.Title = "dXYXYXYXYXYwYsd" + str (random.randint(1,1000000))
    album.save()
    print album.get_statistics (1,2007)

    print "------------------------------------------------------------------------------------------------"
    album = Album.get (session=session, id=3914389)
    new_album = Album.create (session, "This is a test", album.category)
    print "Enter a key to delete the created album"
    raw_input()
    new_album.delete()
    # Get album list
    print "------------------------------------------------------------------------------------------------"
    album_list = Album.get_all(session)
    print "------------------------------------------------------------------------------------------------"

    return

# run main if we're not being imported:
if __name__ == "__main__":
    main()


