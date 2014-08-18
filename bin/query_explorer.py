#!/usr/bin/python
"""Command-line interface for the query language which will print out the
targets to render.  Useful for debugging and general interest."""
from __future__ import print_function
import argparse, sys, pprint, logging, os, urllib
from graph_explorer import graphs
from graph_explorer import preferences
from graph_explorer import config
from graph_explorer.query import Query
from graph_explorer.structured_metrics import StructuredMetrics

def main():
    """Command-line entry point.  Returns exit status."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", help="Graph explorer configuration.")
    parser.add_argument("-e", "--es-host", help="Elasticsearch host.")
    parser.add_argument("--es-port", help="Elasticsearch port.", default=9200)
    parser.add_argument("--index", help="Index name.",)
    parser.add_argument("words", nargs="+")

    cli = parser.parse_args()

    string = u" ".join(cli.words)
    query = Query(string)
    print("Parsed query: {0!r}".format(string))
    pprint.pprint(query)
    print("")

    logging.basicConfig(level=logging.INFO)

    if cli.config_file:
        config.init(cli.config_file)
        settings = config
    else:
        settings = type('Config', (), {})()

    # Bad connection settings cause the process to hang.
    if cli.es_host:
        settings.es_host = cli.es_host
    elif not cli.config_file:
        settings.es_port = "localhost"

    if cli.es_port:
        settings.es_port = cli.es_port
    elif not cli.config_file:
        settings.es_port = 9200

    # No failure if this just doesn't exist.
    if cli.index:
        settings.es_index = cli.index
    elif not cli.config_file:
        settings.es_index = "graphite_metrics2"

    metrics = StructuredMetrics(settings, logging.getLogger())
    _, matching = metrics.matching(query)

    print("Matching metrics:")
    pprint.pprint(matching)
    print("")

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
