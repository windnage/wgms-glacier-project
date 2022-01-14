#!/usr/bin/env python
'''
This script loops through all polygons in an input shapefile and finds ones
that overlap other polygons.  It saves only the overlapping ones -- either just
the first of each pair, or both, according to the --both option.
'''

import os
import argparse
from itertools import combinations
import json

import fiona
from shapely.geometry import shape


def print_arg_summary(args: dict) -> None:
    """Print summary of command-line arguments."""
    print("Arguments object:")
    print(args)


def validated_thresh(x):
    ''' validated_thresh -- validator for the threshold parameter '''
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x


def setup_argument_parser():
    """Set up command line options.  -h or --help for help is automatic"""
    p = argparse.ArgumentParser()
    p.add_argument('-b', '--both', action='store_true', default=False, help="Store both overlapping shapes rather than just one")
    p.add_argument('-i', '--infile', required=True, help='Input shapefile name')
    p.add_argument('-m', '--use_min', action='store_true', default=False, help="Use minimum overlap fraction rather than maximum")
    p.add_argument('-o', '--outfile', default='overlaps.shp',  help='Output shapefile name')
    p.add_argument('-t', '--thresh', type=validated_thresh, default=0.1, help="Threshold of degree of overlap for inclusion")
    p.add_argument('-q', '--quiet', action='store_true', default=False, help="Quiet mode.  Don't print status messages")
    return(p)


def find_overlapping_shapes(polys, thresh=0.1, use_min=False, save_both=False):
    ''' find_overlapping_polys -- find overlapping polygons in the input shapely
    objects and return a list of those entities that overlap.
    '''
    overlapping_shapes = []
    for (p1, p2) in combinations(polys, 2):
        if overlaps(p1, p2, thresh, use_min):
            if p1 not in overlapping_shapes:
                overlapping_shapes.append(p1)
            if save_both:
                if p2 not in overlapping_shapes:
                    overlapping_shapes.append(p2)

    return overlapping_shapes


def overlaps(p1, p2, thresh, use_min):
    ''' Calculate overlap between p1 and p2 subject to the input threshold and
    return True or False
    '''
    geom1 = shape(p1['geometry']).buffer(0)
    geom2 = shape(p2['geometry']).buffer(0)
    inter_area = geom1.intersection(geom2).area
    if use_min:
        lap_fraction = min(inter_area/geom1.area, inter_area/geom2.area)
    else:
        lap_fraction = max(inter_area/geom1.area, inter_area/geom2.area)
    return lap_fraction > thresh


def find_overlaps_in_file(args: dict):
    ''' find_overlaps_in_file -- top-level routine callable with args in simple dictionary
    '''
    with fiona.open(args['infile'], 'r') as f_shapes:
        overlap_shapes = find_overlapping_shapes(f_shapes, thresh=args['thresh'], use_min=args['use_min'], save_both=args['both'])

        print(f"Number of overlapping shapes:  {len(overlap_shapes)}")

        with fiona.open(args['outfile'], 'w',
                crs=f_shapes.crs,
                driver=f_shapes.driver,
                schema=f_shapes.schema,
        ) as out_shapes:
            for p in overlap_shapes:
                out_shapes.write(p)
    return overlap_shapes


def main():
    p = setup_argument_parser()
    args = vars(p.parse_args())

    if not args['quiet']:
        print_arg_summary(args)

    find_overlaps_in_file(args)


if __name__ == '__main__':
    main()