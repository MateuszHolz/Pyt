class SyntaxHighlightings(object):
    rootFrame = None

    outputTags = {
        "red":      "#ff0000",
        "green":    "#00ff00",
        "blue":     "#0000ff",
        "grey":     "#888888",
    }

    # Patterns for telnet output: {{{
    syntaxMsgPrefix = "###"
    syntaxSuccessPrefixes = r'CLAW|SlotMachine'
    syntaxReglistSectionPattern = r'\[\w+\]'
    syntaxReglistValuePattern = r'("[^"]*")|(\s[0-9]+)|(true|false)'

    telnetPatterns = [
        (r'{0}.*$'.format(syntaxMsgPrefix),            "grey"),
        (syntaxReglistValuePattern,                    "grey"),
        (syntaxReglistSectionPattern,                  "blue"),
        (r'^({0}).*$'.format(syntaxSuccessPrefixes),   "green")
    ]
    def telnetOutput():
        listOfCommandPatterns = SyntaxHighlightings.rootFrame.getConfig().getListOfCommandPatterns()
        listOfCommandPatterns = [ (pattern, "blue") for pattern in listOfCommandPatterns ]

        return SyntaxHighlightings.telnetPatterns + listOfCommandPatterns
    # }}}

    # Patterns for TScript output:  {{{
    tscript = [
        ("function",        "red"),
        ("[{}]",            "red"),
        ("#[^\n]*",         "grey"),
        ("'[^']*'",         "blue"),
        ("\|",              "red"),
    ]# }}}

    # Patterns for lua: {{{
    getKeywordPattern = lambda s: r'\y{0}\y'.format(s)
    luaKeywordTag = "red"
    lua = [
        (getKeywordPattern(r'function'), luaKeywordTag),

        # Text:search() method in tkinter uses Tcl regexps
        # \y has the same meaning as \b in Extended Regex
        # http://www.regular-expressions.info/tcl.html
        (getKeywordPattern(r'and'),      luaKeywordTag),
        (getKeywordPattern(r'or'),       luaKeywordTag),
        (getKeywordPattern(r'not'),      luaKeywordTag),

        (getKeywordPattern(r'end'),      luaKeywordTag),
        (getKeywordPattern(r'false'),    luaKeywordTag),
        (getKeywordPattern(r'true'),     luaKeywordTag),
        (getKeywordPattern(r'nil'),      luaKeywordTag),

        (getKeywordPattern(r'if'),       luaKeywordTag),
        (getKeywordPattern(r'else'),     luaKeywordTag),
        (getKeywordPattern(r'elseif'),   luaKeywordTag),
        (getKeywordPattern(r'for'),      luaKeywordTag),
        (getKeywordPattern(r'while'),    luaKeywordTag),
        (getKeywordPattern(r'function'), luaKeywordTag),
        (getKeywordPattern(r'do'),       luaKeywordTag),
        (getKeywordPattern(r'repeat'),   luaKeywordTag),
        (getKeywordPattern(r'return'),   luaKeywordTag),
        (getKeywordPattern(r'then'),     luaKeywordTag),
        (getKeywordPattern(r'until'),    luaKeywordTag),
        (getKeywordPattern(r'break'),    luaKeywordTag),

        (getKeywordPattern(r'in'),       luaKeywordTag),
        (getKeywordPattern(r'local'),    luaKeywordTag),
        (r'"[^"]*"',                     "grey"),
    ]# }}}

    # Patterns for bookmarks: {{{
    bookmarks = [
        ("^[^:]+:",        "blue"),
    ]
    # }}}

    highlightings = {
        "lua"           : lua,
        "tscript"       : tscript,
        "telnetOutput"  : telnetOutput,
        "bookmarks"     : bookmarks
    }

    def setRootFrame(rootFrame):
        SyntaxHighlightings.rootFrame = rootFrame

    def setTags(textWidget):
        for tag, rgb in SyntaxHighlightings.outputTags.items():
            textWidget.tag_configure(tag, foreground=rgb)

    def apply(textWidget, highlighting):
        if highlighting is None:
            return

        highlighter = SyntaxHighlightings.highlightings[highlighting]

        if not isinstance(highlighter, list):
            highlighter = highlighter()

        for (pattern, color) in highlighter:
            textWidget.highlightPattern(pattern, color)
