#######################################################################
# This file is part of Pyblosxom.
#
# Copyright (c) 2010 Menno Smits
# Copyright (c) 2011 Will Kahn-Greene
#
# Pyblosxom is distributed under the MIT license.  See the file
# LICENSE for distribution details.
#######################################################################

"""
Summary
=======

Allows you to break a long entry into a summary and the rest making it
easier to show just the summary in indexes.


Install
=======

This plugin comes with Pyblosxom.  To install, do the following:

1. Add ``Pyblosxom.plugins.readmore`` to the ``load_plugins`` list in
   your ``config.py`` file.

   .. Note::

      If you're using the rst_parser plugin, make sure this plugin
      shows up in load_plugins list before the rst_parser plugin.

      See the rst_parser section below.

2. Configure as documented below.


Configuration
=============

``readmore_breakpoint``

   (optional) string; defaults to "BREAK"

   This is the text that you'll use in your blog entry that breaks the
   body into the summary part above and the rest of the blog entry
   below.

   For example::

      py["readmore_breakpoint"] = "BREAK"

``readmore_template``

   (optional) string; defaults to::

       '<p class="readmore"><a href="%(url)s">read more after the break...</a></p>'

   When the entry is being shown in an index with other entries, then
   the ``readmore_breakpoint`` text is replaced with this text.  This
   text is done with HTML markup.

   Variables available:

   * ``%(url)s``       - the full path to the story
   * ``%(base_url)s``  - base_url
   * ``%(flavour)s``   - the flavour selected now
   * ``%(file_path)s`` - path to the story (without extension)

   .. Note::

      This template is formatted using Python string formatting---not
      Pyblosxom template formatting!


Usage
=====

For example, if the value of ``readmore_breakpoint`` is ``"BREAK"``,
then you could have a blog entry like this::

    First post
    <p>
      This is my first post.  In this post, I set out to explain why
      it is that I'm blogging and what I hope to accomplish with this
      blog.  See more below the break.
    </p>
    BREAK
    <p>
      Ha ha!  Made you look below the break!
    </p>

In order to produce valid HTML, the BREAK needs to be on a line of its
own, i.e. not interspersed in text.

Usage with rst_parser
=====================

Since the rst_parser parses the restructured text and turns it into
HTML and this plugin operates on HTML in the story callback, we have
to do a two-step replacement.

Thus, instead of using BREAK or whatever you have set in
``readmore_breakpoint`` in your blog entry, you use the break
directive::

    First post

    This is my first post.  In this post, I set out to explain why
    it is that I'm blogging and what I hope to accomplish with this
    blog.

    .. break::

    Ha ha!  Made you look below the break!


History
=======

This is based on the original readmore plugin written by IWS years
ago.  It's since been reworked.

Additionally, I folded in the rst_break plugin break directive from
Menno Smits at https://freshfoo.com/wiki/CodeIndex .
"""

__author__ = "Will Kahn-Greene"
__email__ = "willg at bluesock dot org"
__version__ = "2011-11-05"
__url__ = "https://pyblosxom.github.com/"
__description__ = "Breaks blog entries into summary and details"
__category__ = "display"
__license__ = "MIT"
__registrytags__ = "1.5, core"


import re
from Pyblosxom.tools import pwrap


READMORE_BREAKPOINT = "BREAK"
READMORE_TEMPLATE = (
    '<p class="readmore">'
    '<a href="%(url)s">read more after the break...</a>'
    '</p>')


def verify_installation(request):
    config = request.get_configuration()

    for mem in ("readmore_template", "readmore_breakpoint"):
        if mem not in config:
            pwrap("missing optional config property '%s'" % mem)

    return True


def cb_start(args):
    """Register a break directive if docutils is installed."""
    try:
        from docutils import nodes
        from docutils.parsers.rst import directives, Directive
    except ImportError:
        return

    request = args['request']
    config = request.get_configuration()
    breakpoint = config.get("readmore_breakpoint", READMORE_BREAKPOINT)

    class Break(Directive):
        """
        Transform a break directive (".. break::") into the text that
        the Pyblosxom readmore plugin looks for.  This allows blog
        entries written in reST to use this plugin.
        """
        required_arguments = 0
        optional_arguments = 0
        final_argument_whitespace = True
        has_content = False

        def run(self):
            return [nodes.raw("", breakpoint + "\n", format="html")]

    directives.register_directive("break", Break)


def cb_story(args):
    entry = args["entry"]
    if "body" not in entry:
        return

    request = args["request"]
    data = request.get_data()
    config = request.get_configuration()

    breakpoint = config.get("readmore_breakpoint", READMORE_BREAKPOINT)
    template = config.get("readmore_template", READMORE_TEMPLATE)

    """
    Check to see if the breakpoint is in the body.

    Since it might have been wrapped in html tags by a markdown
    plugin, grab everything from the end of breakpoint up to, but
    excluding, either the first opening tag, or newline. We assume
    that all this tag wrapping will stay on the same line.

    We might insist on the breakpoint occurring on the beginning
        of a line of its own.
    """
    match = re.search('(' + breakpoint + ')(.*?)(<[ ]*?[^/].+|[\n])',
                      entry["body"])

    # if not, return because we don't have to do anything
    if not match:
        return

    # if we're showing just one entry, then we show the whole thing
    if data["bl_type"] == 'file':
        entry["body"] = re.sub(breakpoint, "", entry["body"])
        return

    # otherwise we replace the breakpoint with the template
    base_url = config["base_url"]
    file_path = entry["file_path"]

    # Set and use current (or default) flavour for full entry
    flavour = data.get(
        "flavour", config.get("default_flavour", "html"))

    url = '%s/%s.%s' % (base_url, file_path, flavour)

    link = (template % {"url": url,
                        "base_url": base_url,
                        "file_path": file_path,
                        "flavour": flavour})

    entry["just_summary"] = 1
    entry["body"] = entry["body"][:match.start(1)] + link + str(match.group(2))
