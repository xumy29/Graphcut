from collections import deque
import time
from myMaxflow import myMaxflow

def testMyMaxflow():
    g = myMaxflow()
    g.set_nodes(4)
    g.add_edge(0,1,2,2)
    g.add_edge(0,2,5,5)
    g.add_edge(1,3,2,2)
    g.add_edge(2,3,4,4)
    g.add_tedge(0,7,0)
    g.add_tedge(1,5,0)
    g.add_tedge(2,0,2)
    g.add_tedge(3,0,5)
    flow = g.maxflow()
    print("maxflow: ", flow)


def main():
    testMyMaxflow()
    

main()