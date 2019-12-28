# -*- coding: utf-8 -*-

"""download_shakespeare_network_data.py: Download plays written by Shakespeare and create
networks of co-occurring characters (appearances in the same act and scene)."""

__author__ = "Russell J. Funk"
__date__ = "December 22, 2019"

# built in modules
import re
import os
import sys

# other modules
import requests
from bs4 import BeautifulSoup
import networkx as nx
from networkx.algorithms import bipartite

# configuration parameters
BASE_URL = "http://shakespeare.mit.edu/"
OUTPUT_FOLDER = "network_data"

PLAYS = ({"id": "allswell", "name": "All's Well That Ends Well", "type": "comedy"},
         {"id": "asyoulikeit", "name": "As You Like It", "type": "comedy"},
         {"id": "comedy_errors", "name": "The Comedy of Errors", "type": "comedy"},
         {"id": "cymbeline", "name": "Cymbeline", "type": "comedy"},
         {"id": "lll", "name": "Love's Labours Lost", "type": "comedy"},
         {"id": "measure", "name": "Measure for Measure", "type": "comedy"},
         {"id": "merry_wives", "name": "TheMerry Wives of Windsor", "type": "comedy"},
         {"id": "merchant", "name": "The Merchant of Venice", "type": "comedy"},
         {"id": "midsummer", "name": "A Midsummer Night's Dream", "type": "comedy"},
         {"id": "much_ado", "name": "Much Ado About Nothing", "type": "comedy"},
         {"id": "pericles", "name": "Pericles, Prince of Tyre", "type": "comedy"},
         {"id": "taming_shrew", "name": "Taming of the Shrew", "type": "comedy"},
         {"id": "tempest", "name": "The Tempest", "type": "comedy"},
         {"id": "troilus_cressida", "name": "Troilus and Cressida", "type": "comedy"},
         {"id": "twelfth_night", "name": "Twelfth Night", "type": "comedy"},
         {"id": "two_gentlemen", "name": "Two Gentlemen of Verona", "type": "comedy"},
         {"id": "winters_tale", "name": "Winter's Tale", "type": "comedy"},
         {"id": "cleopatra", "name": "Antony and Cleopatra", "type": "tragedy"},
         {"id": "coriolanus", "name": "Coriolanus", "type": "tragedy"},
         {"id": "hamlet", "name": "Hamlet", "type": "tragedy"},
         {"id": "julius_caesar", "name": "Julius Caesar", "type": "tragedy"},
         {"id": "lear", "name": "King Lear", "type": "tragedy"},
         {"id": "macbeth", "name": "Macbeth", "type": "tragedy"},
         {"id": "othello", "name": "Othello", "type": "tragedy"},
         {"id": "romeo_juliet", "name": "Romeo and Juliet", "type": "tragedy"},
         {"id": "timon", "name": "Timon of Athens", "type": "tragedy"},
         {"id": "titus", "name": "Titus Andronicus", "type": "tragedy"})

def main():
 
  # loop over plays
  for play in PLAYS:

    # status
    print("working on %s..." % (play["name"],))

    # initialize a container to store our data
    data_2mode_edges = set()

    # open the index of scenes for the play
    play_index_url = "%s%s/index.html" % (BASE_URL, play["id"])
    play_index_request = requests.get(play_index_url)

    # read the html for the index of scenes
    play_index_html = BeautifulSoup(play_index_request.text, features="lxml")

    # loop over links in scene index 
    for play_index_link in play_index_html.find_all("a", href=True):
    
      # pull out links to scenes
      if play["id"] in play_index_link["href"]:
      
        # pull out act and scene numbers
        assert len(play_index_link["href"].split(".")) == 4
        act_number = int(play_index_link["href"].split(".")[1])
        scene_number = int(play_index_link["href"].split(".")[2])
      
        # open the scene
        scene_url = "%s%s/%s" % (BASE_URL, play["id"], play_index_link["href"])
        scene_request = requests.get(scene_url)
        scene_html = BeautifulSoup(scene_request.text, features="lxml")
      
        # loop over speeches
        for speech in scene_html.find_all("a", {"name" : re.compile("^speech[0-9]+$")}):
        
          # save our data
          actXscene = "%s-%s" % (act_number, scene_number)
          data_2mode_edges.add((speech.text,
                              actXscene))
        
    # create a bipartite graph in networkx
    B = nx.Graph()
    B.add_nodes_from([n[0] for n in data_2mode_edges], bipartite=0)
    B.add_nodes_from([n[1] for n in data_2mode_edges], bipartite=1)
    B.add_edges_from(data_2mode_edges)
  
    # project the network to a unipartite representation
    G = bipartite.generic_weighted_projected_graph(B, [n[0] for n in data_2mode_edges])
    
    # set some graph attributes
    G.graph["source_url"]= play_index_url
    G.graph["play_name"]= play["name"]
    G.graph["play_id"]= play["id"]
    G.graph["play_type"]= play["type"]

    # get rid of node attributes we don't need
    for node in G.nodes:
      del G.nodes[node]["bipartite"]

    # export the graph
    path = os.path.join(os.path.realpath('.'), OUTPUT_FOLDER, "%s.graphml" % (play["id"],))
    nx.write_graphml(G, path)

if __name__ == "__main__":
  main()  