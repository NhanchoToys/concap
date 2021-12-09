"""
a console implement
"""
from __future__ import annotations

from typing import Any, Callable, Optional
from sys import version_info as _pyversion
import argparse

if _pyversion.major == 3:
    if 7 <= _pyversion.minor < 9:
        from typing import List, Dict
    elif _pyversion.minor >= 9:
        List, Dict = list, dict

__version__ = "0.1.0"


class ConsoleArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        if "tree" not in kwargs:
            raise TypeError("'tree' not specified")
        self._console_tree = kwargs.pop("tree")
        super().__init__(*args, **kwargs)

    def parse_args(self, args=None, namespace=None):
        _args, argv = self.parse_known_args(args, namespace)
        if "-h" in args or "--help" in args:
            return None
        if argv:
            msg = ('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
            return None
        return _args

    def _print_message(self, message, _=None):
        if message:
            self._console_tree.print(message)

    def exit(self, status: int = 0, message: Optional[str] = None):
        if message:
            self._print_message(message)

    def error(self, message):
        self.print_usage()
        self.exit(2, ('Error: %s\n') % message)


def command_not_found(tree: "CommandTree", cmd: str, _: str):
    """Internal command-not-found trigger."""
    tree.print(f"{cmd}: command not found")


def logout(tree: "CommandTree"):
    """Internal 'logout' trigger."""
    tree.terminated = True


def input_s(prompt: str = "", interrupt: str = "", eof: str = "logout") -> str:
    """
    Like Python's built-in ``input()``, but it will give a string instead of
    raising an error when a user cancel(^C) or an end-of-file(^D on Unix-like
    or Ctrl-Z+Return on Windows) is received.

      prompt
        The prompt string, if given, is printed to standard output without a
        trailing newline before reading input.
      interrupt
        The interrupt string will be returned when a KeyboardInterrupt occurs.
      eof
        The end-of-file string will be returned when an EOFError occurs.

    Note: This implement keeps trailing a new line even when KeyboardInterrupt
    or EOFError is raised.
    """
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print()
        return interrupt
    except EOFError:
        print()
        return eof


Handler = Callable[["CommandTree", str, str], None]


class CommandTree:
    """
    Command tree for command processing.

      input
        Input function. The function is treadted as ``input_s()`` and should
        receive arguments like it. If not specified, it will be set
        ``input_s`` by default.
      print
        Output function. The function is treated as ``print()`` and should
        receive arguments like it. If not specified, it will be set
        ``print`` by default.

    """
    terminated: bool
    input: Callable[[str, str, str], str]
    print: Callable[[str], None]
    _funcs: Dict[str, Handler]

    def __init__(
        self,
        input: Optional[Callable[[str, str, str], str]] = None,
        output: Optional[Callable[[str], None]] = None
    ):
        def logout_func(tree: CommandTree, cmd: str, arg: str):
            logout(tree)

        self._funcs = {}
        self.terminated = False
        self._funcs["logout"] = logout_func
        self.input = input if input else input_s
        self.print = output if output else print

    def add_command(self, command: str, override: bool = False):
        """
        A decorator that add a command to the CommandTree.

          command
            Command name used for recognising.
          override
            If this argument is True, overriding an existing function is
            allowed. Otherwise, raise a NameError.

        Decorated function should receive these arguments below:
          tree      CommandTree body
          cmd       received command name
          arg       all arguments in a string

        Example:
        >>> tree = console.CommandTree()
        >>> @tree.add_command("hello")
        >>> def hello(tree, cmd, arg):
        >>>     print("Hello world!")
        >>>
        """
        if command in self._funcs and not override:
            raise NameError("command '%s' already exists" % command)

        def _decorator(func: Handler) -> Handler:
            self._funcs[command] = func
            return func
        return _decorator

    def list_command(self) -> List[str]:
        """Return all registered command."""
        return list(self._funcs)

    def find_command(self, keyword: Optional[str] = None) -> List[str]:
        """
        Return a list of command that matches the keyword.

          keyword
            Used for searching command. This works just like
            ``CommandTree.list_command()`` if keyword is omitted.
        """
        cmds = self.list_command()
        if keyword is None:
            return cmds
        result: List[str] = []
        for cmd in cmds:
            if cmd.find(keyword) == 0:
                result.append(cmd)
        return result

    def run_command(self, command: str, arg: str) -> None:
        """
        Run a command that is added to the command tree.

          command
            Command name used for recognising.
          arg
            Argument of the command.

        Example:
        (see previous example code in ``add_command()`` and continue.)
        >>> tree.run_command("hello")
        Hello world!
        >>> tree.run_command("logout")
        >>>
        """
        self._funcs.get(command, command_not_found)(self, command, arg)

    def wait_input(
        self,
        prompt: str = ">>> ",
        interrupt: str = "",
        eof: str = "logout"
    ):
        """Receive an input and process."""
        self.terminated = False
        input_c = self.input(prompt, interrupt, eof)
        cmd, _, arg = input_c.partition(" ")
        if len(cmd) > 0:
            self.run_command(cmd, arg)

    def interactive(
        self,
        prompt: str = ">>> ",
        interrupt: str = "",
        eof: str = "logout"
    ):
        """Run in interactive mode."""
        while not self.terminated:
            self.wait_input(prompt, interrupt, eof)


def argparse_wrapper(parser: argparse.ArgumentParser):
    """
    Wrap function to adapt CommandTree object.

      parser
        Argument parser for parsing args.

    Wrapped function should have these arguments below:
      tree      CommandTree body
      cmd       received command name
      args      parsed arguments from ``argparse.ArgumentParser``
    """
    def _wrapper(f: Callable[[CommandTree, str, Any], None]):
        def __wrapper(tree: CommandTree, cmd: str, arg: str):
            pp = parser.parse_args(arg.split(" "))
            f(tree, cmd, pp)
        # copy function name and docstring
        __wrapper.__name__ = f.__name__
        __wrapper.__doc__ = f.__doc__
        return __wrapper
    return _wrapper
