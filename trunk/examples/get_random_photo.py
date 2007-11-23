#!/bin/python

''' This example will return the URL of a random photograph from a users gallery'''
import smugmugapi as SI
import sys
import logging
import random
from parseargs import CLAP

def get_random_photo (sapi, session_id):
    # get all the abums
    result = sapi.albums_get(SessionID=session_id)
        
    num_albums = len (result.Albums[0].Album)
    album_id = result.Albums[0].Album[random.randint(0,num_albums -1 )]["id"]

    # Now get all the images in the album
    result=sapi.images_get (SessionID=session_id, AlbumID=album_id)

    num_images = len(result.Images[0].Image)
    image_id = result.Images[0].Image[random.randint(0,num_images -1)]["id"]

    result=sapi.images_getURLs (SessionID=session_id, ImageID=image_id)
    # now download the first photo
    large_url = result.Image[0]["LargeURL"]

    return large_url

def get_most_pop_album (sapi, session_id):
    # get all the abums
    result = sapi.albums_get(SessionID=session_id)
        

    album_list = result.Albums[0].Album
    num_albums = len (album_list)
    album_stats={}
#    for album in result.Albums[0].Album:
    for i in range (0, num_albums):
        album = album_list[i]
        result=sapi.albums_getStats (SessionID=session_id, AlbumID=album["id"], Month="1", Year="2007")
        album_stats[album["id"]] = int(result.Album[0]["Medium"])

    rev_items = [(v, k) for k, v in album_stats.items()]
    rev_items.sort()
    print rev_items
    print "Most popular album --->", rev_items[0][1]
    

    return None

def user_login (sapi, email, password):
    ''' create a session for the specified user'''
    result=sapi.login_withPassword (EmailAddress = email, Password = password)
    session_id = result.Login[0].Session[0]["id"]
    return session_id

def handle_args ():
    args = {
        ('-e', '--email'):('email', str, None),
        ('-p', '--password'):('password', str, None),
        ('-m', '--mode'):('mode', str, None),
        ('-d', '--debug'):('debug', bool, False),
        }
    apu = CLAP(sys.argv[1:], args, min_args=2)
    args = apu.check_args()
    return args


def main ():
    smugmug_api_key = "29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"  # API key
    
    # initialize the API

    sapi = SI.SmugMugAPI (smugmug_api_key)
    args = handle_args()

    if args["debug"]:
        SI.set_log_level(logging.DEBUG)

    session_id = user_login (sapi, args['email'], args['password'])
    
    if args["mode"] == "random_photo": # get a random photo
        print get_random_photo(sapi, session_id)
    elif args["mode"] == "popalbum": # get the most popular album
        print get_most_popular_photo(sapi, session_id)

    return

# run the main if we're not being imported:
if __name__ == "__main__":
    main()


