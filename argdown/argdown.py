import argparse as _argparse
# table col
import os as _os
# output
import textwrap as _textwrap

version = '1.0.0'
cols = _os.environ['COLUMNS'] if 'COLUMNS' in _os.environ else 80

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

    argparser = argparse.ArgumentParser(
        description='Markdown export for the argparse module',
        epilog='More info: github.com/9999years/argdown',
        prog=prog
    )

    argparser.add_argument('src_file', nargs='*',
        help='The filename of a Python file to export Markdown from.')

    argparser.add_argument('-', action='store_true', dest='use_stdin',
        help='Read from STDIN instead of a file.')

    argparser.add_argument('--license', action='store_true',
        help='Print license information (MIT) and exit.')

    argparser.add_argument('--usage-header', type=str, default='Usage',
            help='Header text for the `Usage` section.')

    argparser.add_argument('--ref-header', type=str, default='Quick '
            'reference table', help='Header text for the `Quick reference '
            'table` section, a simple table of all the arguments.')

    argparser.add_argument('--args-header', type=str,
            default='Arguments', help='Header text for the `Arguments` '
            'section, a detailed listing of all the arguments.')

    argparser.add_argument(['-s', '--spacey'], action='store_true',
            help='Output a blank line after headers.')

    argparser.add_argument(['-h', '--hide-default'], action='store_true',
            help='Don\'t output default values for the arguments.')

    argparser.add_argument(['-t', '--truncate-help'], action='store_true',
        help='Truncate help in the `Quick reference table` section so that '
        'the table\'s width doesn\'t exceed `--width`. Makes terminal output '
        'prettier but means you\'ll probably have to re-write help messages.')

    argparser.add_argument('--header-depth', type=int, default=1,
        help='Header depth; number of hashes to output before the '
        'top-level header.')

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

    # def md_help(parser, *, depth=1, header='Arguments and Usage',
            # usage_header='Usage', ref_header='Quick reference table',
            # args_header='Arguments', spacey=False, show_default=True,
            # truncate_help=True):

    usage_header  = args.usage_header
    ref_header    = args.ref_header
    args_header   = args.args_header
    spacey        = args.spacey
    show_default  = not args.hide_default
    truncate_help = args.truncate_help
    depth         = args.header_depth

    def gen_help(src):
        md_help()

    if args.use_stdin:
        # catenate stdinput, parse / render
        src = ''
        for line in sys.stdin:
            src += line + '\n'

    # process each file, respecting encoding, although i really hope nobody ever
    # uses that argument and to be quite frank i haven't tested it
    for fname in args.src_file:
        with open(fname, 'r', encoding=args.encoding) as f:
            tree = parser.parsed_data
            print(treetomd(tree, numbering=numbering))
