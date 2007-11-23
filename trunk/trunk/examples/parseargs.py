#!/usr/bin/env python
"""
Utility class for handling of command line arguments, see the bottom of the
file for an example showing how it should be used.
"""
# Copyright: (c) 2006 Muharem Hrnjadovic
# created: 21/11/2006 15:15:49

__version__ = "$Id$"
# $HeadURL $

import sys, getopt, re
import itertools as IT
import operator as OP

class CLAP(object):
    """A class that uses a declarative technique for command line
    argument parsing"""

    def __init__(self, argv, args, min_args = 0, help_string = None):
        """initialiser, just copies its arguments to attributes"""
        self.args = args
        self.min_args = min_args
        self.help_string = help_string
        # skip any leading arguments that don't start with a dash (since
        # this confuses the getopt utility)
        self.argv = list(IT.dropwhile(lambda s: not s.startswith('-'), argv))

    def check_args(self):
        if not self.argv or not self.args or len(self.argv) < self.min_args:
            sys.stderr.write("!! Error: not enough arguments or data " \
                             "for parsing !!\n")
            self.help(1)
            
        self.construct_getopt_data()        
        try:
            opts, args = getopt.getopt(self.argv, self.shortflags,
                self.longflags)
        except getopt.GetoptError, e:
            sys.stderr.write("!! Error: %s !!\n" % str(e))
            self.help(2)
            
        # holds arguments that were actually supplied on the command line
        suppliedd = {}
        # result dictionary
        resultd = {}
        
        # initialise args where approppriate
        try:
            for flags, (argn,typef,initv) in self.args.iteritems():
                if initv is not None: resultd[argn] = typef(initv)
        except Exception, e:
            sys.stderr.write("!! Internal error: %s !!\n" % str(e))
            self.help(3)
            
        # dictionary needed for matching against the command line flags
        matchd = dict([(arg, (OP.itemgetter(0)(v), OP.itemgetter(1)(v))) for \
                       args, v in self.args.iteritems() for arg in args])

        # check the arguments provided on the command line
        try:
            for opt, argv in opts:
                if opt in matchd:
                    argn, typef = matchd[opt]
                    suppliedd[argn] = (typef == bool and True) or typef(argv)
        except Exception, e:
            sys.stderr.write("!! Invalid parameter value: %s !!\n" % str(e))
            self.help(4)

        # merge arguments (supplied on the command line) with the defaults
        resultd.update(suppliedd)
        
        return (resultd)

    def construct_getopt_data(self):
        # pair all flags will their respective types
        flags = [(arg, OP.itemgetter(1)(v)) for args, v in \
                                        self.args.iteritems() for arg in args]
        def ff(((argf, argt), fchar)):
            return argt == bool and argf.lstrip('-') or \
            "%s%s" % (argf.lstrip('-'), fchar)
        # single character flags
        self.shortflags = ''.join(map(ff, zip(filter(lambda t: len(t[0]) <= 2,
                                                     flags), IT.repeat(':'))))
        # multiple character flags
        self.longflags = map(ff, zip(filter(lambda t: len(t[0]) > 2, flags),
                                     IT.repeat('=')))
        
    def help(self, exit_code=0):
        if self.help_string: sys.stderr.write(self.help_string)
        sys.exit(exit_code)

if __name__ == '__main__':
    # please note: the code below is a usage example (modelled on a
    # hypothetical crypto utility)
    
    # dictionary with command line args along with their types and defaults
    args = {
        ('-a', '-x', '--algo')      :   ('algo', str, None),
        ('-c', '--crypt')           :   ('crypt', bool, None),
        ('-d', '--decrypt')         :   ('decrypt', bool, None),
        ('-e', '--echo', '--fyo')   :   ('echo', bool, None),
        ('-l', '--lines')           :   ('lines', int, '25'),
        ('-i', )                    :   ('input', str, None),
        ('-o', )                    :   ('output', str, None),
        ('-p', '--pager', '--pgr')  :   ('pager', str, '/usr/bin/less'),
        ('-r', '--recipient')       :   ('recipient', str, None)
    }
    
    apu = CLAP(sys.argv[1:], args, min_args=2, help_string=__doc__)
    args = apu.check_args()
    print args
