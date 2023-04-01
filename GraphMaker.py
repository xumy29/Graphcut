
import cv2
import numpy as np
from myMaxflow import myMaxflow
import math


class GraphMaker:

    foreground = 1
    background = 0

    seeds = 0
    segmented = 1

    default = 0.5
    MAXIMUM = float('inf') 

    def __init__(self,filename,outfilename):
        self.image = None
        self.graph = None
        self.overlay = None
        self.seed_overlay = None
        self.segment_overlay = None
        self.mask = None
        self.load_image(filename)
        self.background_seeds = []
        self.foreground_seeds = []
        self.background_average = np.array(3)
        self.foreground_average = np.array(3)
        self.nodes = []
        self.edges = []
        self.current_overlay = self.seeds
        self.outfilename = outfilename

    def load_image(self, filename):
        self.image = cv2.imread(filename)
        self.graph = np.zeros_like(self.image)
        self.seed_overlay = np.zeros_like(self.image)
        self.segment_overlay = np.zeros_like(self.image)
        self.mask = None

    def add_seed(self, x, y, type):
        # print(x,y)
        if self.image is None:
            print('Please load an image before adding seeds.')
        if type == self.background:
            if not self.background_seeds.__contains__((x, y)):
                self.background_seeds.append((x, y))
                cv2.rectangle(self.seed_overlay, (x-1, y-1), (x+1, y+1), (0, 0, 255), -1)
        elif type == self.foreground:
            if not self.foreground_seeds.__contains__((x, y)):
                self.foreground_seeds.append((x, y))
                cv2.rectangle(self.seed_overlay, (x-1, y-1), (x+1, y+1), (0, 255, 0), -1)

    def clear_seeds(self):
        self.background_seeds = []
        self.foreground_seeds = []
        self.seed_overlay = np.zeros_like(self.seed_overlay)

    def get_overlay(self):
        if self.current_overlay == self.seeds:
            return self.seed_overlay
        else:
            return self.segment_overlay

    def get_image_with_overlay(self, overlayNumber):
        if overlayNumber == self.seeds:
            return cv2.addWeighted(self.image, 0.9, self.seed_overlay, 0.4, 0.1)
        else:
            return cv2.addWeighted(self.image, 0.9, self.segment_overlay, 0.4, 0.1)

    def create_graph(self):
        if len(self.background_seeds) == 0 or len(self.foreground_seeds) == 0:
            print("Please enter at least one foreground and background seed.")
            return

        print("Making graph") 
        self.graph = np.zeros((self.image.shape[0], self.image.shape[1]))
        print(self.graph.shape)
        self.graph.fill(self.default)
        for coordinate in self.background_seeds:
            self.graph[coordinate[1] - 1, coordinate[0] - 1] = 0
        for coordinate in self.foreground_seeds:
            self.graph[coordinate[1] - 1, coordinate[0] - 1] = 1

        print("Calculating color histogram for background and foreground seeds")
        b_pdf, f_pdf = self.cal_hist()
        # print("b_pdf: ", b_pdf)
        # print("f_pdf: ", f_pdf)

        print("Populating nodes and edges")
        self.populate_graph(b_pdf, f_pdf)

        print("Cutting graph")
        self.cut_graph()

    def cal_hist(self):
        b_bin_width = 10
        b_bins = [0] * (256//b_bin_width+1)
        for coordinate in self.background_seeds:
            p = self.image[coordinate[1]-1, coordinate[0]-1]
            p_gray = int(p[0]*0.114+p[1]*0.587+p[2]*0.299)
            b_bins[p_gray//b_bin_width] += 1
        b_pdf = [0.0] * 256
        for i in range(256):
            width = b_bin_width
            if i >= 250:
                width = 6
            b_pdf[i] = b_bins[i//b_bin_width] / len(self.background_seeds) / width
            b_pdf[i] = max(b_pdf[i], 1e-10) # avoid zero value


        f_bin_width = 10
        f_bins = [0] * (256//f_bin_width+1)
        for coordinate in self.foreground_seeds:
            p = self.image[coordinate[1]-1, coordinate[0]-1]
            p_gray = int(p[0]*0.114+p[1]*0.587+p[2]*0.299)
            f_bins[p_gray//f_bin_width] += 1
        f_pdf = [0.0] * 256
        for i in range(256):
            width = f_bin_width
            if i >= 250:
                width = 6
            f_pdf[i] = f_bins[i//f_bin_width] / len(self.foreground_seeds) / width
            f_pdf[i] = max(f_pdf[i], 1e-10)
            

        return b_pdf, f_pdf
            
        

    def populate_graph(self, b_pdf, f_pdf):
        self.nodes = []
        self.edges = []

        # make all s and t connections for the graph
        for (y, x), value in np.ndenumerate(self.graph):
            # this is a background pixel
            if value == 0.0:
                self.nodes.append((self.get_node_num(x,y,self.image.shape), 0, self.MAXIMUM))
            # this is a foreground node
            elif value == 1.0:
                self.nodes.append((self.get_node_num(x, y, self.image.shape), self.MAXIMUM, 0))
            else:
                p = self.image[y,x]
                p_gray = int(p[0]*0.114+p[1]*0.587+p[2]*0.299)
                self.nodes.append((self.get_node_num(x, y, self.image.shape), -math.log(b_pdf[p_gray]), -math.log(f_pdf[p_gray])))
                # print(-math.log(b_pdf[p_gray]), "    ", -math.log(f_pdf[p_gray]))

        for (y, x), value in np.ndenumerate(self.graph):
            if y == self.graph.shape[0] - 1 or x == self.graph.shape[1] - 1:
                continue
            my_index = self.get_node_num(x, y, self.image.shape)
            neighbor_index = self.get_node_num(x+1, y, self.image.shape)
            
            tmp = -1 * np.sum(np.power(self.image[y, x] - self.image[y, x+1], 2) / 2)
            g = np.exp(tmp) * (1/1)
            # print(tmp, g)
            self.edges.append((my_index, neighbor_index, g))

            neighbor_index = self.get_node_num(x, y+1, self.image.shape)
            tmp = -1 * np.sum(np.power(self.image[y, x] - self.image[y+1, x], 2) / 2)
            g = np.exp(tmp) * (1/1)
            self.edges.append((my_index, neighbor_index, g))

    def cut_graph(self):
        self.segment_overlay = np.zeros_like(self.segment_overlay)
        self.mask = np.zeros_like(self.image, dtype=bool)
        
        #############
        # myMaxflow
        g = myMaxflow()
        g.set_nodes(len(self.nodes))
        #############

        for node in self.nodes:
            g.add_tedge(node[0], node[1], node[2])

        for edge in self.edges:
            g.add_edge(edge[0], edge[1], edge[2], edge[2])

        flow = g.maxflow()
        print("maxflow: ", flow, "type: ", type(flow))
        for index in range(len(self.nodes)):
            if g.get_segment(index) == 1: # 0 means object, 1 means background
                xy = self.get_xy(index, self.image.shape)
                self.segment_overlay[xy[1], xy[0]] = (255, 0, 255)
                self.mask[xy[1], xy[0]] = (True, True, True)



        

    def swap_overlay(self, overlay_num):
        self.current_overlay = overlay_num

    def save_image(self, outfilename):
        if self.mask is None:
            print('Please segment the image before saving.')
            return
        print(outfilename)
        # print(self.image.name())
        to_save = np.zeros_like(self.image)

        np.copyto(to_save, self.image, where=self.mask)
        cv2.imwrite(outfilename, to_save)

    @staticmethod
    def get_node_num(x, y, array_shape):
        return y * array_shape[1] + x

    @staticmethod
    def get_xy(nodenum, array_shape):
        return (nodenum % array_shape[1]), (int(nodenum / array_shape[1]))
