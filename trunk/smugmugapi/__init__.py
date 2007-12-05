#!/usr/bin/python
''' API's to access SmugMug.
For more information - http://code.google.com/p/smugmug-api/

Note: These API's have been inspired by the Flickr API's

What next?

1. Support upload 
2. Add a caching framework to deal with downloaded images
3. More examples
4. Support for keyword based search from feeds
5. Support for last XX pictures in an album
'''

import sys
import urllib
import os.path
import logging
import copy

from xmlnode import XMLNode

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

__version__ = '0.14'
__revision__ = '$Revision: 1 $' # TBD: not too sure if Google will substitute the variable
__all__ = ('SmugMugAPI', 'IllegalArgumentException', 'SmugMugError',
           'XMLNode', 'set_log_level', '__version__', '__revision__')

########################################################################
# Exceptions
########################################################################

class IllegalArgumentException(ValueError):
    '''Raised when a method is passed an illegal argument.
    
    More specific details will be included in the exception message
    when thrown.
    '''

class SmugMugError(Exception):
    '''Raised when a SmugMug method fails.
    
    More specific details will be included in the exception message
    when thrown.
    '''

########################################################################
# SmugMug API's
########################################################################

class SmugMugAPI:
    '''Implements the SmugMug API

    Example sm = SmugMugAPI (apiKey)
    '''

    host = "api.smugmug.com"
    version = "1.2.1"
    rest_path = "/services/api/rest/"


    def __init__ (self, api_key, fail_on_error = True):
        "Create a new flickr instance based on key"
        self.api_key = api_key
        self.fail_on_error = fail_on_error

        self.__handlerCache={}
        return

    def __repr__ (self):
        return ("SmugMug API version %s for key %s" % (SmugMugAPI.version, self.api_key))
    __str__ = __repr__


    def encode_and_sign(self, dictionary):
        '''URL encodes the data in the dictionary, and signs it using the
        given secret.
        '''
        
        #         dictionary = self.make_utf8(dictionary)
        #         dictionary['api_sig'] = self.sign(dictionary)
        return urllib.urlencode(dictionary)
    
    def __getattr__ (self, method):
        '''Handle all the SmugMug Calls'''
        
        # Refuse to act as a proxy for unimplemented special methods
        if method.startswith('__'):
            raise AttributeError("No such attribute '%s'" % method)

        if self.__handlerCache.has_key(method):
            # If we already have the handler, return it
            return self.__handlerCache.has_key(method)

        # Construct the method name and URL
        method = "smugmug." + method.replace("_", ".")
        url = "http://" + SmugMugAPI.host + SmugMugAPI.rest_path + SmugMugAPI.version + "/"

        def handler (**args):
            ''' Dynamically created handler for a SmugMug API call'''
        
            defaults = {'method': method,
                        'APIKey': self.api_key}

            for key, default_value in defaults.iteritems():
                if key in args:
                    del args[key]

            # Step one: Encode the params with fixed position
            postdata_fp = self.encode_and_sign ([("method", method), ("APIKey", self.api_key)])
            # Step 2: Encode the params with variable positions
            postdata = self.encode_and_sign(args)

            postdata = postdata_fp + '&' + postdata

            LOG.debug ("Calling URL: %s?%s" % (url, postdata))

            f = urllib.urlopen(url, postdata)
            data = f.read()
            f.close()
            LOG.debug ("Server returns ...(see below)... \n%s" % (data, ))
            
            result = XMLNode.parseXML(data, True)
            if self.fail_on_error:
                SmugMugAPI.testFailure(result, True)

            return result

        self.__handlerCache[method] = handler

        return self.__handlerCache[method]


    @classmethod
    def testFailure(cls, rsp, exception_on_error=True):
        """Exit app if the rsp XMLNode indicates failure."""
        if rsp['stat'] != "fail":
            return
        
        message = cls.getPrintableError(rsp)
        LOG.error(message)
        
        if exception_on_error:
            raise SmugMugError(message)


    @classmethod
    def getPrintableError(cls, rsp):
        """Return a printed error message string."""
        return "%s: error %s: %s" % (rsp.elementName, \
            cls.getRspErrorCode(rsp), cls.getRspErrorMsg(rsp))
        
    @classmethod
    def getRspErrorCode(cls, rsp):
        """Return the error code of a response, or 0 if no error."""
        if rsp['stat'] == "fail":
            return rsp.err[0]['code']

        return 0

    @classmethod
    def getRspErrorMsg(cls, rsp):
        """Return the error message of a response, or "Success" if no error."""
        if rsp['stat'] == "fail":
            return rsp.err[0]['msg']

        return "Success"



def set_log_level(level):
    '''Sets the log level of the logger used by the FlickrAPI module.
    
    >>> import smugmugapi
    >>> import logging
    >>> smugmugapi.set_log_level(logging.DEBUG)
    '''

    LOG.setLevel(level)

########################################################################
# Test functionality
########################################################################

def main():
    smugmug_api_key = "29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"  # API key
    
    # initialize the API
    set_log_level (logging.DEBUG)
    sapi = SmugMugAPI (smugmug_api_key)
    # login and create a session
    #result=sapi.login_withPassword (EmailAddress = "<your email>", Password = "<password>")
    
    #create an anonymou session
    result=sapi.login_anonymously ()

    # now extract the session
    session_id = result.Login[0].Session[0]["id"]

    # use a random album (from moonriverphotography)
    album_id = "634937"

    # print list of all photos in user selected album
    result=sapi.images_get (SessionID=session_id, AlbumID=album_id)

    image_id = result.Images[0].Image[0]["id"]
    result=sapi.images_getURLs (SessionID=session_id, ImageID=image_id)
    # now download the first photo
    large_url = result.Image[0]["LargeURL"]
    
    print "The first image - %s - of album %s can be accessed here %s" % (image_id, album_id, large_url)

    return
# run the main if we're not being imported:
if __name__ == "__main__":
    main()

