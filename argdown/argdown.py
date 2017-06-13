import argparse as _argparse
# table col
import os as _os
# output
import textwrap as _textwrap

version = '1.1.0'
cols = _os.environ['COLUMNS'] if 'COLUMNS' in _os.environ else 78

def md_help(parser, *, depth=1, header='Arguments and Usage',
        usage_header='Usage', ref_header='Quick reference table',
        args_header='Arguments', spacey=False, show_default=True,
        truncate_help=True):
    global cols
    space = '\n' if spacey else ''
    out = ('#' * depth + f' {header}\n{space}'
        +  '#' * (depth + 1)
        + f' {usage_header}\n{space}'
        f'```\n{parser.format_usage()}```\n\n'
        +  '#' * (depth + 1) + f' {args_header}\n{space}'
        +  '#' * (depth + 2) + f' {ref_header}\n{space}')

    used_actions = {}
    args_detailed = ''

    options = []

    class TableWidths():
        def __init__(self, **kwargs):
            for key, val in kwargs.items():
                setattr(self, key, val)
        def maximize(self, key, val):
            setattr(self, key, max(getattr(self, key), len(val)))

    table = ''
    table_widths = TableWidths(
        short=len('Short'),
        long=len('Long'),
        default=len('Default'),
        help=0
    )

    i = 0
    for k in parser._option_string_actions:
        action = parser._option_string_actions[k]
        # print(repr(action) + '\n')
        this_id = id(action)
        if this_id in used_actions:
            continue
        used_actions[this_id] = True

        options.append({
            'long': '',
            'short': '',
            'default': '',
            'help': action.help
        })

        for opt in action.option_strings:
            # --, long option
            if len(opt) > 1 and opt[1] in parser.prefix_chars:
                table_widths.maximize('long', opt)
                options[i]['long'] = opt
            # short opt
            elif len(opt) > 0 and opt[0] in parser.prefix_chars:
                table_widths.maximize('short', opt)
                options[i]['short'] = opt

        # don't show defaults for options
        default_str = ''
        if (show_default and
            not (isinstance(action.default, bool)
            or isinstance(action, _argparse._VersionAction)
            or isinstance(action, _argparse._HelpAction))):
            default = repr(action.default)
            table_widths.maximize('default', default)
            options[i]['default'] = default
            default_str = f' (Default: {default})'

        args_detailed += ('#' * (depth + 2)
            + ' `' + '`, `'.join(action.option_strings)
            + f'`{default_str}\n{space}'
            + _textwrap.fill(action.help, width=cols) + '\n\n')
        i += 1

    # with proper lengths, we can make the table
    table_widths.help = (cols
        - table_widths.short
        - table_widths.long
        - table_widths.default
        - 4)

    options.insert(0, {
        'short': 'Short',
        'long': 'Long',
        'default': 'Default',
        'help': 'Description'
    })
    options.insert(1, {
        'short':   '-' * table_widths.short,
        'long':    '-' * table_widths.long,
        'default': '-' * table_widths.default,
        'help':    '-' * table_widths.help,
    })
    for opt in options:
        table += (f'|{{short:{table_widths.short}}}|'
            f'{{long:{table_widths.long}}}|'
            f'{{default:{table_widths.default}}}|'
            '{help'
                + (f':.{table_widths.help}' if truncate_help else '')
            + '}\n'
        ).format(**opt)

    out += table + '\n' + args_detailed
    return out

def console():
    prog = 'argdown'
    global cols

    argparser = _argparse.ArgumentParser(
        description='Markdown export for the argparse module',
        prog=prog,
        epilog=
'''Argdown requires a fully formed ArgumentParser object, after all the
add_argument()s have been executed. The only way to make sure the
ArgumentParser object is created in the same way that it would be during normal
script execution is to execute the script until the arguments are parsed. To do
this, argdown reads the input file(s) until it reads a line containing
`.parse_args(`. The rest of the file, being irrelevant to the command-line
invocation, is truncated, and a call to `argdown.md_help()` is inserted to
generate the Markdown from the parser. It is important to note that this means
the whole script up until the call to `parse_args` is executed in its entirety,
including any side-effects that may entail --- argdown does not attempt
to sanitize the code in any way.

More info: github.com/9999years/argdown''')

    argparser.add_argument('src_file', nargs='*',
        help='The filename of a Python file to export Markdown from.')

    argparser.add_argument('-', action='store_true', dest='use_stdin',
        help='Read from STDIN instead of a file.')

    argparser.add_argument('--license', action='store_true',
        help='Print license information (MIT) and exit.')

    argparser.add_argument('--header', type=str,
            default='Arguments and Usage',
            help='Header text for the `Arguments and Usage` section.')

    argparser.add_argument('--usage-header', type=str, default='Usage',
            help='Header text for the `Usage` section.')

    argparser.add_argument('--ref-header', type=str, default='Quick '
            'reference table', help='Header text for the `Quick reference '
            'table` section, a simple table of all the arguments.')

    argparser.add_argument('--args-header', type=str,
            default='Arguments', help='Header text for the `Arguments` '
            'section, a detailed listing of all the arguments.')

    argparser.add_argument('-s', '--spacey', action='store_true',
            help='Output a blank line after headers.')

    argparser.add_argument('-d', '--hide-default', action='store_true',
            help='Don\'t output default values for the arguments.')

    argparser.add_argument('-t', '--truncate-help', action='store_true',
        help='Truncate help in the `Quick reference table` section so that '
        'the table\'s width doesn\'t exceed `--width`. Makes terminal output '
        'prettier but means you\'ll probably have to re-write help messages.')

    argparser.add_argument('--header-depth', type=int, default=1,
        help='Header depth; number of hashes to output before the '
        'top-level header.')

    argparser.add_argument('--encoding', type=str, default='utf-8',
        help='Encoding of all input files. Frankly, there\'s no excuse to ever '
        'use this argument')

    argparser.add_argument('--function', type=str,
        help='Function to be called to parse args. For example, if the '
        'arg-parsing mechanism is contained in a console() function (common if '
        'the script is a module and has a console entry point defined), '
        'enter `--function console` if `console()` must be called to define '
        'the argument parser.')

    argparser.add_argument('-v', '--version', action='version',
        version=f'%(prog)s {version}')

    args = argparser.parse_args()

    if args.license:
        print('''Copyright (c) 2017 Rebecca Turner

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.''')
        exit()

    header        = args.header
    usage_header  = args.usage_header
    ref_header    = args.ref_header
    args_header   = args.args_header
    spacey        = args.spacey
    show_default  = not args.hide_default
    truncate_help = args.truncate_help
    depth         = args.header_depth
    function      = args.function

    import re

    def get_indent(line):
        indent = 0
        for c in line:
            if c == ' ':
                indent += 1
            elif c == '\t':
                indent += 8
            else:
                # break on first word / non-white char
                break
        return indent

    def gen_help(src):
        lines = src.split('\n')
        indent = 0
        for i, line in enumerate(lines):
            if '.parse_args(' in line:
                lastline = i
                # assured to match so no need for checking haha i hope
                parser = re.search(r'(\w+)\.parse_args\(', line).group(1)
                indent = get_indent(line)
                break
        lines = lines[:lastline - 1]
        lines.insert(0, 'import argdown')
        lines.append(' ' * indent +
            f'print(md_help({parser}, depth={depth},\n'
            f'header=\'{header}\', usage_header=\'{usage_header}\',\n'
            f'ref_header=\'{ref_header}\', args_header=\'{args_header}\',\n'
            f'spacey={spacey}, show_default={show_default},\n'
            f'truncate_help={truncate_help}))')
        if function is not None:
            lines.append(function + '()')
        exec('\n'.join(lines))

    if args.use_stdin:
        # catenate stdinput, parse / render
        src = ''
        for line in sys.stdin:
            src += line + '\n'
        gen_help(src)
        exit()

    # process each file, respecting encoding, although i really hope nobody ever
    # uses that argument and to be quite frank i haven't tested it
    for fname in args.src_file:
        with open(fname, 'r', encoding=args.encoding) as f:
            gen_help(f.read())
