#!/usr/bin/python
''' API's to access SmugMug.
For more information - http://code.google.com/p/smugmug-api/'''

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


    def upload(self, filename, callback=None, **arg):
        """Upload a file to flickr.

        Be extra careful you spell the parameters correctly, or you will
        get a rather cryptic "Invalid Signature" error on the upload!

        Supported parameters:

        filename -- name of a file to upload
        callback -- method that gets progress reports
        ByteCount - must match binary byte count
        MD5Sum - md5 of the file
        AlbumID - album in which the photo has to be placed
        ResponseType - either "XML-RPC" or "REST"
        Caption - self explanatory


        The callback method should take two parameters:
        def callback(progress, done)
        
        Progress is a number between 0 and 100, and done is a boolean
        that's true only when the upload is done.
        
        For now, the callback gets a 'done' twice, once for the HTTP
        headers, once for the body.
        """

        if not filename:
            raise IllegalArgumentException("filename must be specified")
        
        # verify key names
        required_params = ('api_key', 'auth_token', 'api_sig')
        optional_params = ('title', 'description', 'tags', 'is_public', 
                           'is_friend', 'is_family')
        possible_args = required_params + optional_params
        
        for a in arg.keys():
            if a not in possible_args:
                raise IllegalArgumentException("Unknown parameter '%s' sent to FlickrAPI.upload" % a)

        arguments = {'auth_token': self.token, 'api_key': self.apiKey}
        arguments.update(arg)

        # Convert to UTF-8 if an argument is an Unicode string
        arg = self.make_utf8(arguments)
        
        arg["api_sig"] = self.sign(arg)
        url = "http://" + FlickrAPI.flickrHost + FlickrAPI.flickrUploadForm

        # construct POST data
        body = Multipart()

        for a in required_params + optional_params:
            if a not in arg: continue
            
            part = Part({'name': a}, arg[a])
            body.attach(part)

        filepart = FilePart({'name': 'photo'}, filename, 'image/jpeg')
        body.attach(filepart)

        return self.send_multipart(url, body, callback)

    def replace(self, filename, photo_id):
        """Replace an existing photo.

        Supported parameters:

        filename -- name of a file to upload
        photo_id -- the ID of the photo to replace
        """
        
        if not filename:
            raise IllegalArgumentException("filename must be specified")
        if not photo_id:
            raise IllegalArgumentException("photo_id must be specified")

        args = {'filename': filename,
                'photo_id': photo_id,
                'auth_token': self.token,
                'api_key': self.apiKey}

        args = self.make_utf8(args)
        args["api_sig"] = self.sign(args)
        url = "http://" + FlickrAPI.flickrHost + FlickrAPI.flickrReplaceForm

        # construct POST data
        body = Multipart()

        for arg, value in args.iteritems():
            # No part for the filename
            if value == 'filename': continue
            
            part = Part({'name': arg}, value)
            body.attach(part)

        filepart = FilePart({'name': 'photo'}, filename, 'image/jpeg')
        body.attach(filepart)

        return self.send_multipart(url, body)

    def send_multipart(self, url, body, progress_callback=None):
        '''Sends a Multipart object to an URL.
        
        Returns the resulting XML from Flickr.
        '''

        LOG.debug("Uploading to %s" % url)
        request = urllib2.Request(url)
        request.add_data(str(body))
        
        (header, value) = body.header()
        request.add_header(header, value)
        
        if progress_callback:
            response = reportinghttp.urlopen(request, progress_callback)
        else:
            response = urllib2.urlopen(request)
        rspXML = response.read()

        result = XMLNode.parseXML(rspXML)
        if self.fail_on_error:
            FlickrAPI.testFailure(result, True)

        return result

########################################################################
# Test functionality
########################################################################

def main():
    smugmug_api_key = "29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"  # API key
    
    # initialize the API

    set_log_level (logging.DEBUG)
    sapi = SmugMugAPI (smugmug_api_key)
    # login and create a session
    result=sapi.login_withPassword (EmailAddress = "", Password = "")

    # now extract the session
    session_id = result.Login[0].Session[0]["id"]
    # print list of all albums
    result = sapi.albums_get(SessionID=session_id)

    # get the first album
    album_id = result.Albums[0].Album[0]["id"]
    # print list of all photos in user selected album
    result=sapi.images_get (SessionID="64d7beceb486536065dbfdc7f666e6a6", AlbumID=album_id)

    image_id = result.Images[0].Image[0]["id"]
    result=sapi.images_getURLs (SessionID="64d7beceb486536065dbfdc7f666e6a6", ImageID=image_id)
    # now download the first photo
    large_url = result.Image[0]["LargeURL"]
    # implement the necessary urllib commands to download the URL
    return

def set_log_level(level):
    '''Sets the log level of the logger used by the FlickrAPI module.
    
    >>> import smugmugapi
    >>> import logging
    >>> smugmugapi.set_log_level(logging.DEBUG)
    '''

    LOG.setLevel(level)


# run the main if we're not being imported:
if __name__ == "__main__":
    main()

