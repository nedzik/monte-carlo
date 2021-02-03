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
@click.option('--lower-bound-column', default='Lower')
@click.option('--upper-bound-column', default='Upper')
@click.option('--experiment-count', default=10000)
@click.option('--distribution-function', default='normal')
@click.option('--triangle-distribution-mode', default=.7)
def forecast(lower_bound_column, upper_bound_column, experiment_count, distribution_function, triangle_distribution_mode):
    filename = 'services.xlsx'
    print(f'Reading {filename} ...')
    data_frame = pd.read_excel(filename, engine='openpyxl')
    data_frame = pd.DataFrame(data_frame, columns=[lower_bound_column, upper_bound_column])
    df = Triangle(triangle_distribution_mode) if distribution_function == 'triangle' else Normal()
    print(f'Using {df.name} distribution function for value selection ...')
    print(f'Running {experiment_count} experiments ...')
    outcomes = [sum([df.pick(j[1], j[2]) for j in data_frame.itertuples()]) for _ in range(experiment_count)]
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
