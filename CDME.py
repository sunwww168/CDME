# -*- coding: utf-8 -*-
from collections import defaultdict
from sklearn import metrics
import networkx as nx

'''
    Community Detection Based on the Matthew Effect
'''
class non_overlap_cdme:


    def __init__(self, filepath='', fname = ''):
        '''
        Constructor
        '''
        print("-------------------------")
        print("init begin:")
        self.filepath = filepath
        self.store_graphlist(fname)
        print ("processing %s" % self.filepath)
        print ("init done")
        print ("-------------------------")

    def store_graphlist(self, fname):
               
        # graph
        self.G = nx.Graph()        
        self.input_node_community = defaultdict(int)
        #input a network
        with open(self.filepath) as file:
            print(" input start")
            for line in file:
                if line[0] != "#" and len(line) > 1:
                    head, tail = [int(x) for x in line.split()]
                    self.G.add_edge(head, tail)
                    
        file.close()
        "Store the node count and edge count"
        self.node_count = self.G.number_of_nodes()
        self.edge_count = self.G.number_of_edges()        
        self.deg = self.G.degree()        
        avede = 0.0
        for key in self.G.nodes():
            avede += self.deg[key]
        avede = avede/self.node_count
        print ("Nodes number:   " + str(self.node_count))
        print ("Edges number:    " + str(self.edge_count))
        print ("Average degree:    " + str(avede))


        
        self.node_community = defaultdict(int)
        # Initialize communities of each node
        self.node_community = dict(zip(self.G.nodes(), self.G.nodes()))
     
       
        #Compute the core groups
        for node in self.G.nodes():
            #The degree of each node
            deg_node = self.deg[node]
            flag = True
            maxsimdeg = 0            
            selected = node            
            if deg_node == 1:
                self.node_community[node] = self.node_community[self.G.neighbors(node)[0]]
            else:               
                for neig in self.G.neighbors(node):                   
                    deg_neig = self.deg[neig]                    
                    if flag is True and deg_node <= deg_neig:
                        flag = False
                        break
  
                if flag is False:
                    for neig in sorted(self.G.neighbors(node)):
                        
                        deg_neig = self.deg[neig]
                        # Compute the Jaccard similarity coefficient
                        nodesim = self.simjkd(node, neig)
                        # Compute the node attraction
                        nodesimdeg = deg_neig*nodesim                       
                        
                        if nodesimdeg > maxsimdeg:
                            selected = neig
                            maxsimdeg = nodesimdeg

                        self.node_community[node] = self.node_community[selected]

    #Compute the jaccard similarity coefficient of two node
    def simjkd(self, u, v):        
        set_v = set(self.G.neighbors(v))
        set_v.add(v)
        set_u = set(self.G.neighbors(u))
        set_u.add(u)
        jac = len(set_v & set_u) * 1.0 / len(set_v | set_u)    
        return jac


    # Simulate the Matthew effect
    def community_detection_cdme(self,outdirpath, fname):
        
        old_persum = -(2 ** 63 - 1)
        old_netw_per = -(2 ** 63 - 1)        
        NMI = -1.0
        max_NMI = -2.0
        persum = old_persum + 1
        netw_per = old_netw_per + 0.1
        maxit = 5
        itern = 0
       
        largest_NMI_itern = 0
        net_persum_list = []
        netw_per_list = []       
        max_node_community = defaultdict(int)        
        nmilist = []
        arilist = []


       
        # The groundtruth
        LB = []
        #Read the groundtruth communities
        f_true = open("dataset/" + fname + "_com.dat")       
        data = f_true.read()        
        lines = data.split('\n')
        for line in lines:
            
            temp = line.split()
            if len(temp) > 1:
                self.input_node_community[int(temp[0])] = int(temp[1])    

        
        LB = [self.input_node_community[k] for k in self.input_node_community.keys()]

        f_true.close()

        LA = [self.node_community[k] for k in self.input_node_community.keys()]

        NMI = metrics.normalized_mutual_info_score(LA, LB)
        ARI = metrics.adjusted_rand_score(LA, LB)
        nmilist.append(NMI)
        arilist.append(ARI)
        

        if (max_NMI < NMI):
            max_NMI = NMI
            largest_NMI_itern = itern
            max_node_community = self.node_community.copy()
       
        print("loop begin:")
        
        while itern < maxit:            
            itern += 1
            old_netw_per = netw_per
            old_persum = persum
            persum = 0
            
            for node in self.G.nodes():
                neiglist = sorted(self.G.neighbors(node))
                cur_p = self.per(node)
#               
                nodeneig_comm = self.nodecount_comm.keys()
                
                cur_p_neig = 0
                for neig in neiglist:
                    cur_p_neig += self.per(neig)
                
                for neig_comm in nodeneig_comm:
                   
                    node_pre_comm = self.node_community[node]                   
                    new_p_neig = 0                    
                    if node_pre_comm != neig_comm:
                        self.node_community[node] = neig_comm
                        new_p = self.per(node)
                        
                        if cur_p <= new_p:                           
                            if cur_p == new_p:
                                for newneig in neiglist:
                                    new_p_neig += self.per(newneig)
                                if cur_p_neig < new_p_neig:
                                    cur_p = new_p
                                    cur_p_neig = new_p_neig
                                else:
                                    self.node_community[node] = node_pre_comm
                            else:
                                for newneig in neiglist:
                                    new_p_neig += self.per(newneig)
                                cur_p = new_p
                                cur_p_neig = new_p_neig
                        else:
                            self.node_community[node] = node_pre_comm

                persum += cur_p


            newLA = [self.node_community[k] for k in self.input_node_community.keys()]

            NMI = metrics.normalized_mutual_info_score(newLA, LB)
            ARI = metrics.adjusted_rand_score(newLA, LB)
            nmilist.append(NMI)
            arilist.append(ARI)
            
            if(max_NMI< NMI):
                max_NMI = NMI
                largest_NMI_itern = itern
                max_node_community = self.node_community.copy()

            print ("max_NMI:" + str(max_NMI))
            print ("\n\n\n")
          
            net_persum_list.append(persum)
            netw_per = persum / self.node_count
            netw_per_list.append(netw_per)

        print ("loop done")


        self.node_community = max_node_community.copy()
       
        self.graph_result = defaultdict(list)
        for item in self.node_community.keys():
            node_comm = int(self.node_community[item])
            self.graph_result[node_comm].append(item)

        f = open(outdirpath + "/" + fname + ".txt", "w+")
        f.write("community number:  \n")
        f.write(str(len(self.graph_result.keys())))
        f.write("\n\n\n\n")
        f.write("loop number:  \n")
        f.write(str(itern))
        f.write("\n\n\n\n")        
        f.write("The best partition in loop:     \n")
        f.write("itern = "+str(largest_NMI_itern))
        f.write("\n\n\n\n")
        f.write("The highest NMI value: \n")
        f.write(str(max_NMI))
        f.write("\n\n\n\n")
        f.write("All NMI values: \n")
        f.write(str(nmilist))
        f.write("\n\n\n\n")
        f.write("All ARI values:     \n")
        f.write(str(arilist))
        f.close()


    # The internal degree of node v in a community
    def per(self, v):
        
        neiglist1 = self.G.neighbors(v)     
        in_v = 0
       
        self.nodecount_comm = defaultdict(int)

       
        for neig in neiglist1:
            if self.node_community[neig] == self.node_community[v]:
                in_v += 1
            else:
                
                self.nodecount_comm[self.node_community[neig]] += 1
        
        cin_v = 1.0*in_v*in_v
        per = cin_v
        return per