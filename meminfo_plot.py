#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from argparse import ArgumentParser


def get_option():
    argparser = ArgumentParser()
    argparser.add_argument('before_file', type=str,
                           help='Before /proc/meminfo file')
    argparser.add_argument('after_file', type=str,
                           help='After /proc/meminfo file')
    argparser.add_argument('output_file', type=str,
                           help='Output file name')
    argparser.add_argument('-y', '--yaxis-ratio', type=float, default=3.0,
                           help='Ratio of y-axis length to x-axis length (default=3.0)')
    argparser.add_argument('-t', '--title', type=str, default="",
                           help='Title string')
    argparser.add_argument('-s', '--show-plot', action='store_true',
                           help='Show plot preview')
    return argparser.parse_args()


def read_meminfo(meminfo_file):
    df = pd.read_csv(meminfo_file, delim_whitespace=True,
                     names=['type', 'value', 'unit'])
    return df


def read_data(before_file, after_file):
    df_before = read_meminfo(before_file).drop('unit', axis=1)
    df_after = read_meminfo(after_file).drop('unit', axis=1)
    df = pd.merge(df_before, df_after, on='type')

    df = df.assign(nvalue_x=(df['value_x']/df['value_x']))
    df = df.assign(nvalue_y=(df['value_y']/df['value_x']))

    # Nan -> 0.0
    df = df.fillna(0.0)

    # inf -> 2.0
    df = df.replace(np.inf, np.nan)
    df = df.fillna(2.0)
    return df


def plot(df, output_file, title, show_plot, yaxis_ratio):
    # style
    xaxis_length = 4
    yaxis_length = 4 * yaxis_ratio
    fig, ax = plt.subplots(figsize=(xaxis_length, yaxis_length))

    # plot
    df.plot.barh(x='type', y=['nvalue_x', 'nvalue_y'], ax=ax,
                 label=['before', 'after'])
    plt.gca().invert_yaxis()

    # legend
    handler1, label1 = ax.get_legend_handles_labels()
    ax.legend(handler1, label1, loc=4, frameon=False, handlelength=2)

    # label
    ax.yaxis.label.set_visible(False)
    ax.set_xlabel('memory usage = (after - before) / before')

    # limit
    ax.axes.set_xlim(0, 2)

    # grid
    ax.grid(True)
    ax.xaxis.grid(linestyle='--')
    ax.yaxis.grid(linestyle='')
    ax.set_axisbelow(True)

    # title
    ax.text(0.96, 0.98, title, horizontalalignment='right',
            transform=ax.transAxes)

    plt.savefig(output_file, dpi=300, bbox_inches="tight", pad_inches=0.1)

    if show_plot:
        plt.show()


def print_table(df):
    pd.set_option("display.precision", 1)
    print(df)


def main():
    args = get_option()
    df = read_data(args.before_file, args.after_file)
    plot(df, args.output_file, args.title, args.show_plot, args.yaxis_ratio)
    print_table(df)


if __name__ == '__main__':
    main()
