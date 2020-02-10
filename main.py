from core import IngredientsAnalysis
from plot import plot_ingredients
from pathlib2 import Path
from utils.helpers import get_config_section, FormatterNoDuplicate
import argparse
import sys
import os

DIR = Path(os.path.abspath(__file__)).parent
FIG_DIR = os.path.join(DIR, 'figures')
if not os.path.isdir(FIG_DIR):
    os.makedirs(FIG_DIR)

CONFIG_FILE = 'config.ini'
PLOTS = ['line', 'bar']
ANALYSIS_TYPE = ['generic', 'route']

def parse_arguments(args_to_parse):
    """
    Parse the command line arguments.

    Params
    ------
    args_to_parse : list of str
            Arguments to parse (split on whitespaces).
    """
    description = "AstraZeneca Coding Exercise"
    default_config = get_config_section([CONFIG_FILE], "Preset")
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=FormatterNoDuplicate)

    # API options
    api = parser.add_argument_group('API specific options')
    api.add_argument('-u', '--base-url', help="Base url for API query",
                          default=default_config['base_url'])
    api.add_argument('-m', '--manufacturer', help='Drug manufacturer',
                          default=default_config['manufacturer'])

    # Plotting options
    plots = parser.add_argument_group('Plot specific options')
    plots.add_argument('-p', '--plot-type',
                       default=default_config['plot_type'], choices=PLOTS,
                       help='Type of plot to produce')
    plots.add_argument('-s', '--save-fig', help='Whether to save the figure',
                       type=bool, default=default_config['save_fig'])

    # Analysis options
    analysis_options = parser.add_argument_group('Anaylsis options')
    analysis_options.add_argument('-a', '--analysis-type', type=str, choices=ANALYSIS_TYPE,
                                  default=default_config['analysis_type'],
                                  help="The type of analysis to undertake")

    args = parser.parse_args(args_to_parse)

    return args


def main(args):
    """
    main function
    """
    url = args.base_url + "\"" + args.manufacturer + "\""
    ingredients_analysis = IngredientsAnalysis(url)
    results = ingredients_analysis.get_analysis(args.analysis_type)

    # display results
    print('****************RESULTS***********************')
    print(results)
    plot_ingredients(results, type=args.plot_type, save_fig=args.save_fig, path=FIG_DIR)


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    main(args)