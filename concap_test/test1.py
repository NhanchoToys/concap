import concap as console

tree = console.CommandTree()
ap = console.ConsoleArgumentParser(tree=tree)

ap.add_argument('-y', '-f', '--force', default=False, action='store_true',
                help='do operation forcefully. only available in '
                'non-interactive mode')
ap.add_argument('-M', '--monochrome', '--nocolor', default=False,
                action='store_true', help="disable color output")


@tree.add_command("hello")
@console.argparse_wrapper(ap)
def hello(tree, cmd, args):
    print(args)


tree.interactive()
