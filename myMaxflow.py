from collections import deque
import warnings

class myMaxflow:
    node_num = 0 # number of nodes, including s and t
    source = -1
    sink = -1
    capacity = [] # capacity table, s is len(capacity)-2, t is len(capacity)-1
    flow = 0.0
    levels = [] 
    segment = [] # segmentation result, segment[i]==0 means the node(pixel) is classified as object, otherwise as background (consistent with the standard library)
    can_reach_sink = []

    def __init__(self):
        pass

    # should be only call once
    def set_nodes(self, node_num):
        self.node_num = node_num + 2 # plus s and t
        self.source = self.node_num - 2
        self.sink = self.node_num - 1
        self.capacity = [{} for i in range(self.node_num)]

    
    def add_edge(self, node1, node2, capacity, r_capacity):
        # print("add_edge ", capacity, type(capacity))
        if node1 < 0 or node1 >= self.node_num - 2 or node2 < 0 or node2 >= self.node_num - 2:
            raise Exception('add_egde: node index is out of scope.')
        self.capacity[node1][node2] = capacity
        self.capacity[node2][node1] = r_capacity
        

    def add_tedge(self, node, s_capacity, t_capacity):
        # if s_capacity > 0 or t_capacity > 0:
        #     print("add_t_edge:", s_capacity, type(s_capacity), t_capacity, type(t_capacity))
        if node < 0 or node >= self.node_num - 2:
            raise Exception('add_tedge: node index is out of scope.')
        # if capacity == 0, it's the same as no edge between these two nodes
        if s_capacity > 0:
            # since we will always begin traversing from source node, there is
            # no need to add edge from node to source node, the sink node is similar.
            self.capacity[self.source][node] = s_capacity
        if t_capacity > 0:
            self.capacity[node][self.sink] = t_capacity

        
    def maxflow(self):
        self.flow = 0
        while(True):
            sink_level = self.bfs()
            if sink_level == 0:
                break
            path = []
            flow = self.dfs(self.source, float('inf'), path, sink_level)
            # if flow < 0.01:
            #     break
            self.flow = self.flow + flow

        return self.flow
    
            
    def bfs(self):
        self.levels = [0] * self.node_num
        queue = deque()
        queue.append(self.source)
        self.levels[self.source] = 1

        level_cnt = {}
        level_cnt[1] = 1
        reach_sink_cnt = 0
        father = [-1] * self.node_num
        self.can_reach_sink = [False] * self.node_num
        self.can_reach_sink[self.sink] = True

        break_level = -1
        while queue:
            cur = queue.popleft()
            if break_level != -1 and self.levels[cur] == break_level:
                break
            for nei, cap in self.capacity[cur].items():
                if cap > 0 and nei == self.sink:
                    break_level = self.levels[cur] + 1
                    reach_sink_cnt += 1
                    tmp = cur
                    while(tmp != -1):
                        self.can_reach_sink[tmp] = True
                        tmp = father[tmp]
                if self.levels[nei] == 0 and cap > 0:
                    father[nei] = cur
                    self.levels[nei] = self.levels[cur] + 1

                    if self.levels[nei] not in level_cnt:
                        level_cnt[self.levels[nei]] = 0
                    level_cnt[self.levels[nei]] += 1


                    queue.append(nei)
        
        if self.levels[self.sink] > 0:
            print("cur flow: ", self.flow)
            print("bfs: sink node is in level", self.levels[self.sink])
            # print("total nodes: ", len(self.levels))
            print("bfs: number of paths that reaches sink: ", reach_sink_cnt)
            print()

        # print("print level tables: ")
        # print(level_cnt)

        return self.levels[self.sink] 
    
    def dfs(self, cur, cur_max_inbound, path, sink_level):
        # print("sink_level: ", sink_level, "path: ", path, "cur_inbound: ", cur_max_inbound)
        if cur_max_inbound <= 0:
            return 0
        if cur == self.sink:
            # print("reach sink, cur_inbound: ", cur_max_inbound, self.levels[self.sink])
            # print("path: ", path)
            return cur_max_inbound
        cur_outbound = 0
        for nei, cap in self.capacity[cur].items():
            if self.levels[nei] == self.levels[cur] + 1 and self.levels[nei] <= sink_level and cap > 0:
                flow = self.dfs(nei, min(cur_max_inbound - cur_outbound, cap), path + [nei], sink_level)
                self.capacity[cur][nei] -= flow
                if nei != self.sink and cur != self.source:
                    self.capacity[nei][cur] += flow
                cur_outbound += flow
                # if cur_outbound > 0:
                #     return cur_outbound
        
        return cur_outbound
    

    
    def get_segment(self, node_index):
        if node_index < 0 or node_index >= self.node_num - 2:
            raise Exception('get_segment: node index is out of scope.')
        if len(self.segment) == 0:
            self.set_object_nodes()

        return self.segment[node_index]

    def set_object_nodes(self):
        self.segment = self.node_num * [1]
        queue = deque()
        queue.append(self.source)
        while queue:
            cur = queue.popleft()
            for nei, cap in self.capacity[cur].items():
                if self.segment[nei] == 1 and cap == 0:
                    queue.append(nei)
                    self.segment[nei] = 0
        
        


        


                


                

        

        
     

     


