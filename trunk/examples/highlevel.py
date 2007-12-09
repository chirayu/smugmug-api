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
        self.id = result.Login[0].Session[0]["id"]
        SI.set_log_level(logging.DEBUG)
        return

    def logout ():
        return

########################################################################
class SmugBase (object):
    def __init__ (self, **args):
        self.__load_required = False
        self.__def_gets = {}

        # assign None/default values to all the variables
        # TODO : Change None to appropriate construct to derive the default value 
        for var in self.__class__._readonly.iterkeys():
            setattr (self, "__"+var, None )                
        for var in self.__class__._readwrite.iterkeys():
            setattr (self, var, None)
        for var in self.__class__._all_foreign_keys.iterkeys():
            setattr (self, var, None)
        setattr (self, self.__class__._primary_key[0], None)
            
        # now assign the arguments
        for a in args.iterkeys():
            if a in self.__class__._readonly_vars:
                raise AttributeError("The attribute %s is read-only." % a)
            elif a in self.__class__._readwrite_vars:
                setattr (self, a, args[a])
            elif a in self.__class__._all_foreign_keys_vars:
                setattr (self, a, args[a])
            elif a in self.__class__._primary_key[0]:
                setattr (self, a, args[a])
            else:
                raise AttributeError("The attribute %s is unknown." % a)
        return

    def __repr__ (self):
        return "%s : %s" % (self.__class__.__name__, getattr (self, self.__class__._primary_key[0]))
    __str__ = __repr__

    @classmethod
    def get (cls, session, id):
        ''' This method is a hack as there is no way to enquire the site statistics '''
        return cls(session=session, id=id)


########################################################################
class Highlight (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported


########################################################################
class Community (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported


########################################################################
class Category (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {'Name':{},}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

    @classmethod
    def get_all (cls, session, NickName=None, SitePassword=None):
        try:
            result = session.api.categories_get(SessionID=session.id, NickName=NickName, 
                                                SitePassword=SitePassword)
            category_list = []
            for category in result.Categories[0].Category:
                category_list.append(Category (session = session, id=category["id"], 
                                               Name=category["Name"]))
            return category_list
        except:
            raise
                                     
    @classmethod
    def get (cls, session, id):
        ''' This method is a hack as there is no way to enquire the site statistics '''
        print "-0-0-0-0-0-0"
        category_list = Category.get_all(session)
        print category_list
        for category in category_list:
            print category.id, id
            if category.id == id:
                return category
        raise AttributeError #TBD

    @classmethod
    def create (cls, session, Name):
        result = session.api.categories_create (SessionID=session.id, Name=Name)
        return (Category(session=session, id=id, Name=Name)) # there is no way to fetch the category

    def delete (self):
        result = session.api.categories_delete (SessionID=self.session.id, CategoryID=self.id)
        return

    def save (self):
        ''' Will be mainly used for renames '''
        result = session.api.categories_rename (SessionID=self.session.id, CategoryID=self.id, Name=self.Name),
        return
        
    
        
########################################################################
class SubCategory (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class Album (SmugBase):

    # Meta descriptors - default, variable, class

    _readonly = {'LastUpdated':{},}
    _readonly_vars = _readonly.keys()

    _readwrite = {'Position': {}, 
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
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {'session': {"class": Session, "variable":"SessionID"},
                               'category': {"class": Category, "variable":"CategoryID"},}

    _null_foreign_keys = {'subcategory':{"class": SubCategory, "variable":"SubCategoryID"},
                           'highlight':{"class": Highlight, "variable":"HighlightID"},
                           'community':{"class": Community, "variable":"CommunityID"},}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()


    _primary_key = ["id"] # only one primary key is supported



#     def __setattr__(self, key, value):
# #         if key in self.__class__._readonly_vars:
# #             raise AttributeError("The attribute %s is read-only." % key)
# #         else: # not checking if the attribute is present in the other lists. It is too much of an overhead
#             super(Album, self).__setattr__(key, value)


    def _load_properties(self):
        """Loads the properties from SmugMug."""
        self.__load_required = False
        try:
            result = self.session.api.albums_getInfo(SessionID=self.session.id, AlbumID=self.id)
            for prop in self._readwrite.iterkeys():
                setattr (self, prop, result.Album[0][prop])
            for prop in self._readonly.iterkeys():
                setattr (self, prop, result.Album[0][prop])
            for prop in self._all_foreign_keys.iterkeys():
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

        if getattr (self, self.__class__._primary_key[0]) == None:
            raise AttributeError("Mandatory primary_key %s is required." % prop)            
         # check if the non null foreign_keys are input
        for prop in self._non_null_foreign_keys:
            if getattr(self, prop) is None:
                raise AttributeError("Mandatory foreign_key %s is required." % prop)

        args = {}
        for prop in self._readwrite:
            args [prop] = getattr (self, prop)
            
        # TODO use the var meta data
        args["AlbumID"] = self.id
        args["SessionID"] = self.session.id
        args["CategoryID"] = self.category.id
        args["SubCategoryID"] = self.subcategory.id
        args["CommunityID"] = self.community.id
        args["HighlightID"] = self.highlight.id

        result = self.session.api.albums_changeSettings (**args)
        return

    @classmethod
    def create (cls, session, Title, category, **args):
        
        result = session.api.albums_create (SessionID=session.id, Title=Title, 
                                            CategoryID=category.id)
        return #TBD
    
    @classmethod
    def get_all (cls, session, NickName=None, Heavy=None, SitePassword=None):
        result = session.api.albums_get (SessionID=session.id, NickName=NickName, 
                                         Heavy=Heavy, SitePassword=SitePassword)
        album_list=[]
        for album in result.Albums[0].Album:
            album_list.append(Album(session=session, id=album["id"]))
        return album_list

    @classmethod
    def get (cls, session, id):
        try:
            result = session.api.albums_getInfo(SessionID=session.id, AlbumID=id)
            a = Album (session=session, id=id)
            for prop in cls._readwrite.iterkeys():
                setattr (a, prop, result.Album[0][prop])
            for prop in cls._readonly.iterkeys():
                setattr (a, prop, result.Album[0][prop])
                
            a.category = Category.get (session=a.session, id=result.Album[0].Category[0]["id"])
            a.subcategory = SubCategory.get (session=a.session, id=result.Album[0].SubCategory[0]["id"])
            a.highlight = Highlight.get (session=a.session, id=result.Album[0].Highlight[0]["id"])
            a.community = Community.get (session=a.session, id=result.Album[0].Community[0]["id"])
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
        response = self.session.api.albums_getStats (SessionID=self.session.id, 
                                                     AlbumID = self.id, Month=Month, 
                                                     Year=Year, Heavy=Heavy)

        reply = {}
        reply["Bytes"] = response.Album[0]["Bytes"]
        reply["Tiny"] = response.Album[0]["Tiny"]
        reply["Thumb"] = response.Album[0]["Thumb"]
        reply["Small"] = response.Album[0]["Small"]
        reply["Medium"] = response.Album[0]["Medium"]
        reply["Large"] = response.Album[0]["Large"]
        reply["Original"] = response.Album[0]["Original"]
        return reply
    

########################################################################
class Family (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################        
class Friends (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class Orders (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class PropPricing (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class Styles (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class ShareGroups (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class Themes (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class User (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class WaterMarks (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class Image (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {'Caption': {},
                  'Position':{},
                  'Serial':{},
                  'Size':{},
                  'Width':{},
                  'Height':{},
                  'LastUpdated':{},
                  'FileName':{},
                  'MD5Sum':{},
                  'Watermark':{},
                  'Format':{},
                  'Keywords':{},
                  'Date':{},
                  'AlbumURL':{},
                  'TinyURL':{},
                  'ThumbURL':{},
                  'SmallURL':{},
                  'MediumURL':{},
                  'LargeURL':{},
                  'XLargeURL':{},
                  'X2LargeURL':{},
                  'X3LargeURL':{},
                  'OriginalURL':{},
                  }
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys ={'session': {"class": Session, "variable":"SessionID"},
                             'album': {"class": Category, "variable":"AlbumID"},}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported

########################################################################
class AlbumTemplates (SmugBase):
    _readonly = {}
    _readonly_vars = _readonly.keys()

    _readwrite = {}
    _readwrite_vars = _readwrite.keys()

    _non_null_foreign_keys = {}
    _null_foreign_keys = {}

    _all_foreign_keys = _non_null_foreign_keys
    _all_foreign_keys.update(_non_null_foreign_keys)    
    _all_foreign_keys_vars = _all_foreign_keys.keys()

    _primary_key = ["id"] # only one primary key is supported
        


def main ():
    
    session = Session (SI.SmugMugAPI("29qIYnAB9zHcIhmrqhZ7yK7sPsdfoV0e"), email = '', password = '')

    print [Album (session=session, id=10), Album (session=session, id=11)]

    # get the test album
    album = Album.get (session=session, id=3914389)
    print album.Position
    import random
    album.Title = "dXYXYXYXYXYwYsd" + str (random.randint(1,1000000))
    album.save()
    print album.get_statistics (1,2007)

    new_album = Album.create (session, "This is a test", album.category)

    # Get album list
    album_list = Album.get_all(session)
    print album_list

# run main if we're not being imported:
if __name__ == "__main__":
    main()
    
