#!/bin/python

''' This example will return the URL of a random image from a users gallery'''
import smugmugapi as SI
import sys
import logging
import random
import urllib
import os
from optparse import OptionParser

def get_albums (sapi, session_id, nick):
    # get all the abums
    result = sapi.users_getTree(SessionID=session_id, NickName=nick)
    return 

def get_random_image (sapi, session_id):
    # get all the abums
    result = sapi.albums_get(SessionID=session_id)

    num_albums = len (result.Albums[0].Album)
    album_id = result.Albums[0].Album[random.randint(0,num_albums -1 )]["id"]

    # Now get all the images in the album
    result=sapi.images_get (SessionID=session_id, AlbumID=album_id)

    num_images = len(result.Images[0].Image)
    image_id = result.Images[0].Image[random.randint(0,num_images -1)]["id"]

    result=sapi.images_getURLs (SessionID=session_id, ImageID=image_id)

    large_url = result.Image[0]["LargeURL"]

    return large_url

def get_most_pop_album (sapi, session_id):
    # get all the abums
    result = sapi.albums_get(SessionID=session_id)


    album_list = result.Albums[0].Album
    num_albums = len (album_list)
    album_stats={}

    for album in album_list:
        result=sapi.albums_getStats (SessionID=session_id, AlbumID=album["id"], Month="1", Year="2007")
        album_stats[album["id"]] = int(result.Album[0]["Medium"])

    rev_items = [(v, k) for k, v in album_stats.items()]
    rev_items.sort()
    print rev_items
    print "Most popular album --->", rev_items[0][1]

def download_image (sapi, session_id, image_id, path):
    result=sapi.images_getURLs (SessionID=session_id, ImageID=image_id)
    tiny_url = result.Image[0]["TinyURL"]

    urllib.urlretrieve (tiny_url, os.path.join(path, image_id + "-Ti.jpg"))
    return

def download_album (sapi, session_id, album_id, path):
    """ download a complete album """
    result = sapi.albums_get(SessionID=session_id)

    result=sapi.images_get (SessionID=session_id, AlbumID=album_id)
    num_images = len(result.Images[0].Image)
    image_list = result.Images[0].Image

    for image in image_list:
        download_image (sapi, session_id, image["id"], path)

    return None

def user_login (sapi, email, password):
    ''' create a session for the specified user'''
    result=sapi.login_withPassword (EmailAddress = email, Password = password)
    session_id = result.Login[0].Session[0]["id"]
    return session_id

def init_parser ():

    parser = OptionParser(usage="%prog -m MODE [-e EMAIL] [-p PASSWORD] [-n NICKNAME] [-o OUTPUTDIR]  [-d]", version="%prog 1.0")

    parser.add_option("-e", "--email",
                      action="store", type="string", dest="email",
                      help="XYZ")
    parser.add_option("-p", "--password",
                      action="store", type="string", dest="password",
                      help="XYZ")

    parser.add_option("-m", "--mode",
                      action="store", type="choice", dest="mode",
                      choices=["random_image", "pop_album", "download_album_tiny", "get_albums"],
                      help="Specify one mode: random_image, pop_album, download_album_tiny, get_albums")

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enable debugging [default: %default]")

    parser.add_option("-a", "--album",
                      action="store", type="int", dest="album",
                      help="Specify album")

    parser.add_option("-o", "--output",
                      action="store", type="string", dest="output",
                      help="Output directory")

    parser.add_option("-n", "--nick",
                      action="store", type="string", dest="nick",
                      help="Nickname (only to be used with mode get_albums)")

    return parser


def main ():
    smugmug_api_key = "29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"  # API key

    # initialize the API

    sapi = SI.SmugMugAPI (smugmug_api_key)
    parser = init_parser()
    (options, args) = parser.parse_args()
    if options.debug:
        SI.set_log_level(logging.DEBUG)

    session_id = user_login (sapi, options.email, options.password)

    if options.mode == "random_image": # get a random image
        print get_random_image(sapi, session_id)
    elif options.mode == "pop_album": # get the most popular album
        print get_most_pop_album(sapi, session_id)
    elif options.mode == "download_album_tiny": # get the most popular album
        print download_album(sapi, session_id, options.album, options.output)
    elif options.mode == "get_albums": # get the most popular album
        print get_albums(sapi, session_id, options.nick)

    return

# run the main if we're not being imported:
if __name__ == "__main__":
    main()


