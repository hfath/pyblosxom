# vim: tabstop=4 shiftwidth=4
"""
This module contains the base class for all the Entry classes.
"""
import time

CONTENT_KEY = "content"

class EntryBase:
    """
    EntryBase is the base class for all the Entry classes.  Each 
    instance of an Entry class represents a single entry in the weblog, 
    whether it came from a file, or a database, or even somewhere off 
    the InterWeeb.
    """
    def __init__(self):
        self._data = None
        self._metadata = {}

    def getData(self):
        """
        Returns the data string.  This method should be overridden to
        provide from pulling the data from other places.

        @returns: the data as a string
        @rtype: string
        """
        return str(self._data)

    def setData(self, data):
        """
        Sets the data content for this entry.  If you are not
        creating the entry, then you have no right to set the data
        of the entry.  Doing so could be hazardous depending on what
        EntryBase subclass you're dealing with.

        @param data: the data
        @type  data: string
        """
        self._data = data

    def getId(self):
        """
        This should return an id that's unique enough for caching 
        purposes.

        Override this.

        @returns: string id
        @rtype: string
        """
        return ""

    def setTime(self, timeTuple):
        """
        This takes in a given time tuple and sets all the magic metadata
        variables we have according to the items in the time tuple.

        @param timeTuple: the timetuple to use to set the data with--this
            is the same thing as the mtime/atime portions of an os.stat.
        @type  timeTuple: tuple of ints
        """
        self['timetuple'] = timeTuple
        self['ti'] = time.strftime('%H:%M',timeTuple)
        self['mo'] = time.strftime('%b',timeTuple)
        self['mo_num'] = time.strftime('%m',timeTuple)
        self['da'] = time.strftime('%d',timeTuple)
        self['yr'] = time.strftime('%Y',timeTuple)
        self['fulltime'] = time.strftime('%Y%m%d%H%M%S',timeTuple)
        # YYYY-MM-DDThh:mm:ssTZD
        self['w3cdate'] = time.strftime('%Y-%m-%dT%H:%M:%S%Z',timeTuple)
        self['date'] = time.strftime('%a, %d %b %Y',timeTuple)

    def __getitem__(self, key, default=None):
        """
        Retrieves an item from this dict based on the key given.  If 
        the item does not exist, then we return the default.  If the 
        item is CONTENT_KEY then we return the result from 
        self.getData().

        @returns: the value of self._metadata.get(key, default) or 
            self.getData()
        @rtype: varies
        """
        if key == CONTENT_KEY:
            return self.getData()
        return self._metadata.get(key, default)

    def __setitem__(self, key, value):
        """
        Sets the metadata[key] to the given value.

        Note: using the key CONTENT_KEY is probably not a good idea.

        @param key: the given key name
        @type key: varies

        @param value: the given value
        @type value: varies
        """
        self._metadata[key] = value

    def __delitem__(self, key):
        del self._metadata[key]

    def has_key(self, key):
        """
        Returns whether a given key is in the metadata dict.  If the key
        is the CONTENT_KEY, then we automatically return true.

        @param key: the key to check in the metadata dict for
        @type  key: varies

        @returns: whether (1) or not (0) the key exists
        @rtype: boolean
        """
        if key == CONTENT_KEY:
            return 1
        return self._metadata.has_key(key)

    def keys(self):
        """
        Returns a list of the keys that can be accessed through
        __getitem__.

        @returns: list of key names
        @rtype: list of varies
        """
        return self._metadata.keys() + [CONTENT_KEY,]