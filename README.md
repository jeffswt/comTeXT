
# comTeXT

## Overview

### Philosophy

comTeXT is a language created by [jeffswt](https://github.com/jeffswt), which
is intended to be as extensible and feasible as is easy-to-read and
easy-to-write.

Extensibility and portability, however, is emphasized above all else. A
comTeXT-formatted document should be publishable to the web or to publications
as-is, without having to deal with target-related elements that's been marked
up with native tags or formatting instructions. While comTeXT's syntax has been
influencd by LaTeX, it itself is mainly oriented towards web publishing.

### Publishing

comTeXT's syntax is intended for one purpose only: to be used as a format for
writing for the web and the paper only once.

comTeXT is not a replacement for HTML or LaTeX, instead, it relies on these two
for rendering and publishing. It's builtin syntax is tiny, compared to that
of HTML and LaTeX. Thanks to the *comTeXT Syntax Library (cSTL)*, most common
functions can be invoked directly in comTeXT using LaTeX grammar. The idea for
comTeXT is to make it easy to port from source to web or paper, and easily
extensible. Note that comTeXT is both a publishing format and a writing format.
Thus, comTeXT's formatting syntax addresses issues that can be conveyed in
word processing softwares, but does not address issues directly related to page
formatting.

For any markup that is not covered by the Syntax Library, simply create a
function to process it. You may not inline HTML or LaTeX elements directly into
the document, as this not only breaks the parser mechanisms, it also violates
the design philosophy.

## Mechanism

### Parsing

The comTeXT parser processes the document in linear sequence, and treats every
letter, space, line break or function as an element in a DOM-like model. The
parsing process looks like this:

 1. When a line had just ended, check if this line matches single-line symbol
    patterns. If so, execute this.
 2. Check if the current position leads a function. If so, parse it.
 3. If it happens to be a space or a break, send it to process auto break.
 4. Pass the character on to output.

When dealing with scope (`{...}` and others that do not begin and end with
breackets) contents, there are two types of parsing methods, namely:

 1. Verbatim, which gets the exact content between the brackets.
 2. Parsable, which parses the contents between the brackets.

Functions will be repeatedly parsed after execution until there are no more
to process (in the current state).

The parser will process the document twice, the first to process all macros,
and the second to convert the document to the target format. Please note that
functions that works only during the second phase would be parsed but not
executed during the first phase.

### Auto-break

Two or more line breaks are treated as a paragraph break.

Leading or trailing spaces and breaks in the document are ignored.

Spaces and breaks around the begin and end markers of scopes, when not being
the case of leading and trailing in the document, are not ignored but rather
counted as a single space.

When a function is at the root level of the document, it may also decide
whether it is contained in a paragraph or not.

## Builtin Functions

### Front Matter

**Note: This section will be eventually replaced with YAML.**

An optional header can be placed at the beginning of the document with leading
spaces and breaks. The headers would not be displayed in the output, but can be
retrieved from the class if invoked as a module instead of a command line
program.

The header is initiated and terminated with a line of hyphens (`-`). Header
entries and entry contents are separated with a vertical line (`|`). When a
certain header entry remains empty, it indicates that the current contents
follow those above this line. The first entry should not be empty, and vertical
lines need not be aligned.

For an example, see the code below:

```
-------------------------------------------------------------------------------
 title     | Sword Art Online 17:
           | Alicization Awakening
 author    | Kawahara Reki
 publisher | Kadokawa
-------------------------------------------------------------------------------
```

Which produces the following output:

```json
{
    "title": "Sword Art Online 17: Alicization Awakening",
    "author": "Kawahara Reki",
    "publisher": "Kadokawa"
}
```

### Comments

Comments works similar to the way LaTeX comments works. When text is commented,
they would not be visible in the output.

Single line comments start with a percentage sign (`%`) and ends at the same
line. For example:

```tex
% This is a single-line comment
```

### Loading Libraries

A library, literally, is another comTeXT file which contains a number of
functions (a wider concept of function, including commands, environments and
symbols). Only the functions in the library would be loaded into the main
file.

The library name (or module name) is specified as an argument, and the
corresponding file ending with the extensions `.ctx`, `.tex` and `.sty` would
be searched sequentially in the include paths.

Libraries can be loaded in two ways, the first is specifying the library name
inside the comTeXT source file, like this:

```tex
\usepackage{stdlib}
```

The second way is preloading it before parsing the source. This can only be
achieved in module mode (invoking comTeXT parser through a program).

```py
result = parse_file('./readme.ctx', 'web', preload_libs=['stdlib',])
```

Re-importing of the same module even in different files is allowed.
