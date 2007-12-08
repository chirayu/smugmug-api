# Copyright (c) 2007 by the respective coders, see
# http://code.google.com/p/smugmug-api/
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import smugmugapi as SI
import logging 

########################################################################
class Session (object):
    def __init__ (self, api, email=None, password=None, fail_on_error = True):
        if email is not None and password is not None:
            result = api.login_withPassword (EmailAddress = email, Password = password)
        else:
            result = api.login_anonymously ()
        
        self.api = api
        self.SessionID = result.Login[0].Session[0]["id"]
        SI.set_log_level(logging.DEBUG)
        return

    def logout ():
        return

########################################################################

########################################################################
class Highlight (object):
    def __init__ (self, session, HighlightID, **args):
        self.session = session
        self.HighlightID = HighlightID
        return

########################################################################
class Community (object):
    def __init__ (self, session, CommunityID, **args):
        self.session = session
        self.CommunityID = CommunityID
        return


########################################################################
class Category (object):
    def __init__ (self, session, CategoryID, **args):
        self.session = session
        self.CategoryID = CategoryID
        return
        
########################################################################
class SubCategory (object):
    def __init__ (self, session, CategoryID, SubCategoryID, **args):
        self.session = session
        self.SubCategoryID = SubCategoryID
        return

########################################################################
class Album (object):

    # Meta descriptors - default, variable, class

    __readonly = {'LastUpdated':{},}
    __readonly_vars = __readonly.keys()

    __readwrite = {'Position': {}, 
                   'ImageCount': {}, 
                   'Title': {}, 
                   'Description': {}, 
                   'Keywords': {}, 
                   'Public': {}, 
                   'Password': {}, 
                   'PasswordHint': {}, 
                   'Printable': {}, 
                   'Filenames': {}, 
                   'Comments': {}, 
                   'External': {}, 
                   'Originals': {}, 
                   'EXIF': {}, 
                   'Share': {}, 
                   'SortMethod': {}, 
                   'SortDirection': {}, 
                   'FamilyEdit': {}, 
                   'FriendEdit': {}, 
                   'HideOwner': {}, 
                   'CanRank': {}, 
                   'Clean': {}, 
                   'Geography': {}, 
                   'SmugSearchable': {}, 
                   'WorldSearchable': {}, 
                   'X2Larges': {}, 
                   'X3Larges': (),
                   }
    __readwrite_vars = __readwrite.keys()

    __non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},
                               'category': {"class": Category, "variable":"CategoryID"},}

    __null_foreign_keys = {'subcategory':{"class": SubCategory, "variable":"SubCategoryID"},
                           'highlight':{"class": Highlight, "variable":"HighlightID"},
                           'community':{"class": Community, "variable":"CommunityID"},}

    __all_foreign_keys = __non_null_foreign_keys
    __all_foreign_keys.update(__non_null_foreign_keys)    
    __all_foreign_keys_vars = __all_foreign_keys.keys()


    __primary_key = ["id"] # only one primary key is supported


    def __init__ (self, **args):
        self.__load_required = False
        self.__def_gets = {}

        # assign None/default values to all the variables
        # TODO : Change None to appropriate construct to derive the default value 
        for var in self.__class__.__readonly.iterkeys():
            setattr (self, "__"+var, None )                
        for var in self.__class__.__readwrite.iterkeys():
            setattr (self, var, None)
        for var in self.__class__.__all_foreign_keys.iterkeys():
            setattr (self, var, None)
        setattr (self, self.__class__.__primary_key[0], None)
            
        # now assign the arguments
        for a in args.iterkeys():
            if a in self.__class__.__readonly_vars:
                raise AttributeError("The attribute %s is read-only." % a)
            elif a in self.__class__.__readwrite_vars:
                setattr (self, a, args[a])
            elif a in self.__class__.__all_foreign_keys_vars:
                setattr (self, a, args[a])
            elif a in self.__class__.__primary_key[0]:
                setattr (self, a, args[a])
            else:
                raise AttributeError("The attribute %s is unknown." % a)
        return

    def __repr__ (self):
        return "%s : %s" % (self.__class__.__name__, getattr (self, self.__class__.__primary_key[0]))
    __str__ = __repr__

    def __setattr__(self, key, value):
#         if key in self.__class__.__readonly_vars:
#             raise AttributeError("The attribute %s is read-only." % key)
#         else: # not checking if the attribute is present in the other lists. It is too much of an overhead
            super(Album, self).__setattr__(key, value)


    def _load_properties(self):
        """Loads the properties from SmugMug."""
        self.__load_required = False
        try:
            result = self.session.api.albums_getInfo(SessionID=self.session.SessionID, AlbumID=self.id)
            for prop in self.__readwrite.iterkeys():
                setattr (self, prop, result.Album[0][prop])
            for prop in self.__readonly.iterkeys():
                setattr (self, prop, result.Album[0][prop])
            for prop in self.__all_foreign_keys.iterkeys():
                setattr (self, prop, result.Album[0][prop])
                
            # now set the foreign keys
#             self.category = Category (self.session, result.Album[0].Category[0]["id"])
#             self.subcategory = SubCategory (self.session, self.category, result.Album[0].SubCategory[0]["id"])
#             self.highlight = Highlight (self.session, result.Album[0].Highlight[0]["id"])
#             self.community = Community (self.session, result.Album[0].Community[0]["id"])
        except:
            self.__load_required = True
            raise
        return
                
    def save(self):

        if getattr (self, self.__class__.__primary_key[0]) == None:
            raise AttributeError("Mandatory primary_key %s is required." % prop)            
         # check if the non null foreign_keys are input
        for prop in self.__non_null_foreign_keys:
            if getattr(self, prop) is None:
                raise AttributeError("Mandatory foreign_key %s is required." % prop)

        args = {}
        for prop in self.__readwrite:
            args [prop] = getattr (self, prop)
            
        # TODO use the var meta data
        args["AlbumID"] = self.id
        args["SessionID"] = self.session.SessionID
        args["CategoryID"] = self.category.CategoryID
        args["SubCategoryID"] = self.subcategory.SubCategoryID
        args["CommunityID"] = self.community.CommunityID 
        args["HighlightID"] = self.highlight.HighlightID

        result = self.session.api.albums_changeSettings (**args)
        return

    @classmethod
    def create (cls, session, Title, Category, **args):
        
        result = session.api.albums_create (SessionID=session, Title=Title, 
                                            CategoryID = category.CategoryID)
        return
    
    @classmethod
    def get_all (cls, session, NickName=None, Heavy=None, SitePassword=None):
        result = session.api.albums_get (SessionID=session.SessionID, NickName=NickName, 
                                         Heavy=Heavy, SitePassword=SitePassword)
        album_list=[]
        for album in result.Albums[0].Album:
            album_list.append(Album(session=session, id=album["id"]))
        return album_list

    @classmethod
    def get (cls, session, id):
        try:
            result = session.api.albums_getInfo(SessionID=session.SessionID, AlbumID=id)
            a = Album (session=session, id=id)
            for prop in cls.__readwrite.iterkeys():
                setattr (a, prop, result.Album[0][prop])
            for prop in cls.__readonly.iterkeys():
                setattr (a, prop, result.Album[0][prop])
                
            
            a.category = Category (a.session, a.category, result.Album[0].Category[0]["id"])
            a.category.def_load()
            a.subcategory = SubCategory (a.session, a.category, result.Album[0].SubCategory[0]["id"])
            a.subcategory.def_load()
            a.highlight = Highlight (a.session, result.Album[0].Highlight[0]["id"])
            a.highlight.def_load()
            a.community = Community (a.session, result.Album[0].Community[0]["id"])
            a.community.def_load()
        except:
            raise
        return a

    def def_load (self):
        self.__load_required == True
        return

    def delete (self):
        return

    def resort (self, By, Direction):
        return

    def upload ():
        return

    def get_statistics (self, Month=None, Year=None, Heavy=None):
        response = self.session.api.albums_getStats (SessionID=self.session.SessionID, 
                                                     AlbumID = self.id, Month=Month, 
                                                     Year=Year, Heavy=Heavy)

        reply = ()
        reply["Bytes"] = response.Album[0]["Bytes"]
        reply["Tiny"] = response.Album[0]["Tiny"]
        reply["Thumb"] = response.Album[0]["Thumb"]
        reply["Small"] = response.Album[0]["Small"]
        reply["Medium"] = response.Album[0]["Medium"]
        reply["Large"] = response.Album[0]["Large"]
        reply["Original"] = response.Album[0]["Original"]
        return reply
    

########################################################################
class Family (object):
    def __init__ (self, session, FamilyID, **args):
        return

########################################################################        
class Friends (object):
    def __init__ (self, session, FriendID, **args):
        return

########################################################################
class Orders (object):
    def __init__ (self, session):
        return

########################################################################
class PropPricing (object):
    def __init__ (self, session):
        return

########################################################################
class Styles (object):
    def __init__ (self, session):
        return

########################################################################
class ShareGroups (object):
    def __init__ (self, session):
        return

########################################################################
class Themes (object):
    def __init__ (self, session):
        return

########################################################################
class User (object):
    def __init__ (self, session):
        return

########################################################################
class WaterMarks (object):
    def __init__ (self, session):
        return

########################################################################
class Image (object):
    def __init__ (self, session, ImageID, **args):
        return
        

########################################################################
class AlbumTemplates (object):
    def __init__ (self, session, AlbumTemplateID, **args):
        return
        


def main ():
    
    session = Session ()

    print [Album (session=session, id=10), Album (session=session, id=11)]

    # Get album list
    album_list = Album.get_all(session)
    print album_list

    # get the test album
    album = Album.get (session=session, id=3914389)
    print album.Position
    print "==================================XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    import random
    album.Title = "dXYXYXYXYXYwYsd" + str (random.randint(1,1000000))
    album.save()
    print album.get_statistics (1,2007)

    new_album = Album.create (session, "This is a test", album.category)
    

# run main if we're not being imported:
if __name__ == "__main__":
    main()
    
