#!/usr/bin/env python

import click
import random

import pandas as pd
from scipy.stats import norm


# TODO: Experimental
class Triangle:
    def __init__(self, mode) -> None:
        super().__init__()
        self.mode = float(mode)
        self.name = f'triangle (with {self.mode:.2f} mode)'

    def pick(self, lower, upper):
        value, lower, upper, mode = random.random(), float(lower), float(upper), lower + (upper - lower) * self.mode
        return value * (mode - lower) + lower if value < self.mode else value * (upper - mode) + mode


class Normal:
    def __init__(self) -> None:
        super().__init__()
        self.name = 'normal'

    # noinspection PyMethodMayBeStatic
    def pick(self, lower, upper):
        value, lower, upper = random.random(), float(lower), float(upper)
        mean, std = lower + (upper - lower)/2, (upper - lower)/3.29
        return norm.ppf(value, loc=mean, scale=std)


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('-l', '--lower-bound-column', 'lower', default='Lower', show_default=True)
@click.option('-u', '--upper-bound-column', 'upper', default='Upper', show_default=True)
@click.option('-c', '--experiment-count', 'count', default=10000, type=int, show_default=True)
@click.option('-f', '--distribution-function', 'function', default='normal', show_default=True)
@click.option('--td-mode', default=.7, type=float, show_default=True)
def forecast(filename, lower, upper, count, function, td_mode):
    print(f'Reading {filename} ...')
    data_frame = pd.read_excel(filename, engine='openpyxl')
    data_frame = pd.DataFrame(data_frame, columns=[lower, upper])
    data_frame = data_frame.dropna()
    df = Triangle(td_mode) if function == 'triangle' else Normal()
    print(f'Using {df.name} distribution function for value selection ...')
    print(f'Running {count} experiments ...')
    outcomes = [sum([df.pick(j[1], j[2]) for j in data_frame.itertuples()]) for _ in range(count)]
    summary = pd.DataFrame({'effort': outcomes}).describe(percentiles=[.025, 0.05, 0.075, 0.925, 0.95, .975])
    ci_95_lower = next(summary.filter(regex=r'^2\.5%$', axis=0).itertuples()).effort
    ci_95_upper = next(summary.filter(regex=r'^97\.5%$', axis=0).itertuples()).effort
    ci_90_lower = next(summary.filter(regex='^5%$', axis=0).itertuples()).effort
    ci_90_upper = next(summary.filter(regex='^95%$', axis=0).itertuples()).effort
    ci_85_lower = next(summary.filter(regex='^7.5%$', axis=0).itertuples()).effort
    ci_85_upper = next(summary.filter(regex='^92.5%$', axis=0).itertuples()).effort
    print(f'95% CI - [{ci_95_lower:.2f}, {ci_95_upper:.2f}] days')
    print(f'90% CI - [{ci_90_lower:.2f}, {ci_90_upper:.2f}] days')
    print(f'80% CI - [{ci_85_lower:.2f}, {ci_85_upper:.2f}] days')


if __name__ == '__main__':
    forecast()
