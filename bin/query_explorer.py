#!/usr/bin/python
"""Command-line interface for the query language which will print out the
targets to render.  Useful for debugging and general interest."""
from __future__ import print_function
import argparse, sys, pprint, logging, os, urllib
from graph_explorer import graphs
from graph_explorer.query import Query
from graph_explorer.structured_metrics import StructuredMetrics

def main():
    """Command-line entry point.  Returns exit status."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--es-host", help="Elasticsearch host.")
    parser.add_argument("--es-port", help="Elasticsearch port.", default=9200)
    parser.add_argument("--index", help="Index name.", default="graph_explorer")
    parser.add_argument("words", nargs="+")

    cli = parser.parse_args()

    string = u" ".join(cli.words)
    query = Query(string)
    print("Parsed query: {0!r}".format(string))
    pprint.pprint(query)
    print("")

    logging.basicConfig(level=logging.INFO)

    # Hax.  Better to load from app config and allow cli overrides.  Also if the
    # syntax is wrong then the program will hang, or if any of these valeus are
    # missing then StructuredMetrics object will have no attribute for the es
    # server.
    config = type('Config', (), {})()
    config.es_host = cli.es_host
    config.es_port = cli.es_port
    # No failure if this just doesn't exist.
    config.es_index = cli.index

    metrics = StructuredMetrics(config, logging.getLogger())
    _, matching = metrics.matching(query)

    print("Matching metrics:")
    pprint.pprint(matching)
    print("")

    # Hax.  Use proper object for whatever this is
    preferences = type("Preferences", (), {})()
    preferences.graph_options = {}

    built, _ = graphs.build_from_targets(matching, query, preferences)

    print("Targets:")
    for _, graph in built.iteritems():
        pprint.pprint(graph)
    print("")

    print("Render url:")

    for _, graph in built.iteritems():
        url = "http://graphite/render/"
        targets = urllib.urlencode([('target', target['target'])
                                     for target in graph['targets']])
        query = "".join(targets)
        print("http://graphite/render/?{0}".format(query))

    return 0

if __name__ == "__main__":
    sys.exit(main())
