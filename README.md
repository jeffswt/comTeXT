
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
of HTML and LaTeX. Thanks to the *comTeXT Standard Library (cSTL)*, most common
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
letter, space, line break, command or environment as an element in a DOM-like
model. The parsing process looks like this:

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

An optional front matter can be placed at the beginning of the document with
leading spaces and breaks. The headers would not be displayed in the output,
but can be retrieved from the class if invoked as a module.

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

### Defining Commands

Users may create their own commands with the function `\newcommand`. A command
looks like this:

```tex
\foo{Lorem ipsum dolor sit amet}{consectetur adipiscing elit}
```

The new command function takes in 2 arguments. The first specifies the function
and its call parameters, which is a series of parameters separated by
semicolons, following a function name separated by a colon, like this:

```
function_name: parameter; parameter; ...; parameter
```

#### Parameters

Parameters have many types, namely the following:

 1. Language and arguments, where argument names are separated with commas.
    Supported languages are:
     *  Python (`py`)
     *  Substitute with plain text (`raw`)
    The parameter looks like this: `language(argument, argument, ...)`
 2. Convertion target. When target does not match, this function would not
    be imported. Modes include:
     *  Preprocess block (`ctx->ctx`)
     *  Convert block to HTML (`ctx->web`)
     *  Convert block to print (`ctx->doc`)
 3. Autobreak mode. This parameter only takes effect when under the root
    node (not contained in any function). Modes include:
     *  Inside paragraph preferred (`wrapinblk`, default)
     *  Outside paragraph preferred (`leaveblk`)

#### Arguments

Arguments may be composed of arbitrary Unicode characters, except the
following listed, or space:

```
!"#$%&\'()*+,-./:;<=>?[\]^_`{|}~
```

An argument can be taken in as *Verbatim* or *Parsable*, depending on the need.
Normally the argument would be taken in as parsable, but when an asterisk (`*`)
is placed ahead of the argument name, it would be specified as verbatim (like
`*argument`).

#### Code in Python

We provided an interface for defining functions in Python. All argument types
are strings, and the result returned by your function should also be a string.

You may access variables independent from this instance (similar to global
variables) by specifying `glob.*`. Before using them, you must invoke the
function `glob.initvar(name, value)` to declare this variable. This declaration
is only executed once.

If a variable needs to be shared between functions, you should use `univ.*.*`
instead. Before using, the function `univ.initvar(scope, name, value)` must be
invoked to declare the variable. The scope name can be arbitrary.

#### Code with templates

Substituting the text of a template with arguments work better than hard-coding
functions in real-world programming languages under certain simpler scenarios.
Global or universal variables do not apply to templates. But arguments still
work. You can indicate an argument replacement by adding a `#` mark before
the argument name (like `#argument`).

An example can be seen as following:

```tex
\newcommand{count: py(add_to, splitter); ctx->ctx; wrapinblk}{
    # initialize the variables
    glob.initvar('cnt', 0)
    univ.initvar('count_vars', 'cnt', 1)
    # process result
    res = str(glob.cnt) + splitter + str(univ.count_vars.cnt)
    # apply counter
    glob.cnt += int(add_to)
    univ.count_vars.cnt += 1
    # return result
    return res
}
\newcommand{get_count: py(); ctx->ctx; wrapinblk}{
    # initialize the variables, in case it is undefined
    univ.initvar('count_vars', 'cnt', 1)
    # returning non-string types are also okay, but they would
    # be forcefully converted to strings afterwards
    return str(univ.count_vars.cnt)
}
\newcommand{foo: raw(*text); ctx->web}{
    % 'text' is a verbatim argument
    <span style="font-weight: bold;">#text</span>
}
```

Bracket positions and break positions must strictly follow the example.

### Defining Environments

Users may create their own commands with the function `\newenvironment`. An
environment looks like this:

```tex
\begin{bar}{param}
Lorem ipsum dolor sit amet, consectetur adipiscing elit
\end{bar}
```

Environment definitions are similar to command definitions. But there are a few
limitations:

 1. At least 1 argument must be taken.
 2. The last argument must be verbatim.

You can specify an environment in this way:

```tex
\newenvironment{bar: raw(style, *text); ctx->ctx}{
    <span style="#style">#text</span>
}
```

### Paragraphs

Alongside the auto-breaking mechanism, you can also use the `\paragraph{...}`
command to enforce a paragraph break.

### Escaped Characters

Some characters have special meanings in comTeXT. When trying to display those
characters, you need to escape them.

| Command              | Purpose                  |
|:---------------------|:-------------------------|
| `\\`                 | Backslash (`\`)          |
| `\ ` (Escaped space) | Whitespace (1 character) |
| `\%`                 | Percentage sign (`%`)    |
| `\{`                 | Left bracket (`{`)       |
| `\}`                 | Right bracket (`}`)      |
| `\$`                 | Dollar sign (`$`)        |
 
## Standard Library (cSTL)

Not yet implemented.

## Installation

Not yet implemented.

## License

```
MIT License

Copyright (c) 2018 Geoffrey Tang.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
