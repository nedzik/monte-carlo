#!/usr/bin/env python

import logging
import random
import sys
from random import random

import click
import pandas as pd
from click import progressbar
from scipy.stats import norm

LOGGING_FORMAT = '''%(asctime)s — %(levelname)s — %(message)s'''
LOGGING_LEVELS = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}


class Triangle:
    def __init__(self, mode) -> None:
        super().__init__()
        self.mode = float(mode)
        self.name = f'triangle (with {self.mode:.2f} mode)'

    def pick(self, lower, upper):
        lower, upper, mode = float(lower), float(upper), lower + (upper - lower) * self.mode
        def left(): return max(random(), random()) * (mode - lower) + lower
        def right(): return min(random(), random()) * (upper - mode) + mode
        return left() if random() < self.mode else right()


class Normal:
    def __init__(self) -> None:
        super().__init__()
        self.name = 'normal'

    # noinspection PyMethodMayBeStatic
    def pick(self, lower, upper):
        value, lower, upper = random(), float(lower), float(upper)
        mean, std = lower + (upper - lower)/2, (upper - lower)/3.29
        return norm.ppf(value, loc=mean, scale=std)


def read_data_from_excel(filename, sheet_name, filter_expression, lower, upper):
    try:
        logging.info(f'''Reading {filename}, sheet '{sheet_name if sheet_name else 'default'}' ...''')
        data_frame = pd.read_excel(filename, engine='openpyxl', sheet_name=(sheet_name if sheet_name else 0))
        logging.info(f'''Read {len(data_frame)} rows.''')
        logging.info(f'''Removing rows where '{upper}' value is not greater than '{lower}' value ...''')
        data_frame = data_frame[data_frame[lower] < data_frame[upper]]
        logging.info(f'''Retained {len(data_frame)} rows.''')
        if filter_expression:
            logging.info(f'''Applying filter expression '{filter_expression}' ''')
            column, value = filter_expression.split('==')
            data_frame = data_frame[data_frame[column.strip()] == f'{value.strip()}']
            logging.info(f'''Retained {len(data_frame)} rows.''')
        logging.info(f'''Trimming the data set to '{lower}' and '{upper}' columns ...''')
        data_frame = pd.DataFrame(data_frame, columns=[lower, upper])
        logging.info(f'''Retained {len(data_frame)} rows.''')
        logging.info(f'''Removing rows with NaN values in the '{lower}' and '{upper}' columns ...''')
        data_frame = data_frame.dropna()
        logging.info(f'''Retained {len(data_frame)} rows.''')
        return data_frame
    except KeyError as e:
        logging.critical(f'{e}. Aborting ...')
        sys.exit(1)


def run_experiments(data_frame, distribution_function, count):
    logging.info(f'Using {distribution_function.name} distribution function for value selection ...')
    logging.info(f'Running {count} experiments ...')
    with progressbar(range(count)) as bar:
        return [sum([distribution_function.pick(j[1], j[2]) for j in data_frame.itertuples()]) for _ in bar]


def print_results(outcomes):
    summary = pd.DataFrame({'effort': outcomes}).describe(percentiles=[.025, 0.05, 0.075, 0.925, 0.95, .975])
    ci_95_lower = next(summary.filter(regex=r'^2\.5%$', axis=0).itertuples()).effort
    ci_95_upper = next(summary.filter(regex=r'^97\.5%$', axis=0).itertuples()).effort
    ci_90_lower = next(summary.filter(regex='^5%$', axis=0).itertuples()).effort
    ci_90_upper = next(summary.filter(regex='^95%$', axis=0).itertuples()).effort
    ci_85_lower = next(summary.filter(regex='^7.5%$', axis=0).itertuples()).effort
    ci_85_upper = next(summary.filter(regex='^92.5%$', axis=0).itertuples()).effort
    print(f'''95% CI - [{ci_95_lower:.2f}, {ci_95_upper:.2f}] days''')
    print(f'''90% CI - [{ci_90_lower:.2f}, {ci_90_upper:.2f}] days''')
    print(f'''80% CI - [{ci_85_lower:.2f}, {ci_85_upper:.2f}] days''')


HELP_FUNCTION = '''Distribution function to use (normal, triangle). The default is 'normal' '''


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('-f', '--filter-expression', help="""A simple filter like ColumnName == Value""")
@click.option('-l', '--lower-bound-column', 'lower', default='Lower', show_default=True)
@click.option('-u', '--upper-bound-column', 'upper', default='Upper', show_default=True)
@click.option('-c', '--experiment-count', 'count', default=10000, type=int, show_default=True)
@click.option('-d', '--distribution-function', 'function', default='normal', help=HELP_FUNCTION)
@click.option('-s', '--sheet_name', help='Sheet name (or the first sheet by default)')
@click.option('-m', '--triangle-distribution-mode', 'td_mode', default=.7, type=float, show_default=True)
@click.option('-v', '--verbose', default=2, count=True, show_default=True)
def forecast(filename, filter_expression, lower, upper, count, function, td_mode, sheet_name, verbose):
    logging.basicConfig(level=LOGGING_LEVELS.get(verbose, 2), format=LOGGING_FORMAT, datefmt='%H:%M:%S')
    data_frame = read_data_from_excel(filename, sheet_name, filter_expression, lower, upper)
    outcomes = run_experiments(data_frame, Triangle(td_mode) if function == 'triangle' else Normal(), count)
    print_results(outcomes)
    logging.info(f'Done.')


if __name__ == '__main__':
    forecast()
