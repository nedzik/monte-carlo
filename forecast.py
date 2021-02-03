#!/usr/bin/env python

import click
import random

import pandas as pd


class TriangularDistribution:
    def __init__(self, mode) -> None:
        super().__init__()
        self.mode = float(mode)

    # =IF(RAND()<B8,MAX(RAND(),RAND())*(B4-B5)+B5,MIN(RAND(),RAND())*(B3-B4)+B4)
    def pick(self, low, high):
        value, low, high, mode = random.random(), float(low), float(high), low + (high - low) * self.mode
        return value * (mode - low) + low if value < self.mode else value * (high - mode) + mode


@click.command()
@click.option('--low-bound-column', default='Low')
@click.option('--high-bound-column', default='High')
@click.option('--experiment-count', default=1000)
def forecast(low_bound_column, high_bound_column, experiment_count):
    filename = 'services.xlsx'
    print(f'Reading {filename} ...')
    df = pd.read_excel(filename, engine='openpyxl')
    df = pd.DataFrame(df, columns=[low_bound_column, high_bound_column])
    td = TriangularDistribution(0.6)
    print(f'Running {experiment_count} experiments ...')
    outcomes = [sum([td.pick(j[1], j[2]) for j in df.itertuples()]) for i in range(experiment_count)]
    summary = pd.DataFrame({'effort': outcomes}).describe(percentiles=[.025, .975])
    ci_lower = next(summary.filter(like='2.5%', axis=0).itertuples()).effort
    ci_upper = next(summary.filter(like='97.5%', axis=0).itertuples()).effort
    print(f'95% CI - [{ci_lower:.2f}, {ci_upper:.2f}]')


if __name__ == '__main__':
    forecast()
