import ast
import argparse
import configparser

def get_config_section(filenames, section):
    """Return a dictionary of the section of `.ini` config files. Every value
    int the `.ini` will be literally evaluated, such that `l=[1,"as"]` actually
    returns a list.
    """
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.optionxform = str
    files = parser.read(filenames)
    if len(files) == 0:
        raise ValueError("Config files not found: {}".format(filenames))
    dict_session = dict(parser[section])
    dict_session = {k: ast.literal_eval(v) for k, v in dict_session.items()}
    return dict_session

class FormatterNoDuplicate(argparse.ArgumentDefaultsHelpFormatter):
    """Formatter overriding `argparse.ArgumentDefaultsHelpFormatter` to show
    `-e, --epoch EPOCH` instead of `-e EPOCH, --epoch EPOCH`
    Note
    ----
    - code modified from cPython: https://github.com/python/cpython/blob/master/Lib/argparse.py
    """

    def _format_action_invocation(self, action):
        # no args given
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)
            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    # don't store the DEFAULT
                    parts.append('%s' % (option_string))
                # store DEFAULT for the last one
                parts[-1] += ' %s' % args_string
            return ', '.join(parts)