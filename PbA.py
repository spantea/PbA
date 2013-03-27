import cProfile
from igraph import *
from igraph import Graph
import random

class PbA:
    
    def __init__(self):
        self.g = Graph(1)
        self.g.vs[0]['name'] = 'start'
        self.g.vs[0]['index'] = 99
        self.g.vs[0]['let'] = ''
        self.g.vs[0]['pron'] = ''
        
    def loadDict(self,dictName):
        wordDict = {}
    
        myDict = open(dictName)
    
        for line in myDict:
            key = line.split()[0]
            value = line.split()[1]
            wordDict[key] = value
    
        return wordDict
    
    """----------------------------------------------------------------------------------------------------------
        PARTIAL MATCH FUNCTION
        INPUT: 
            myWord - the word for which we compute the pronunciation
            dict_entry - the word from the dictionary
            pron - pronunciation of the dictionary entry
        
        str1 represent the larger string, while str2 is the smaller string which needs to be shifted to the righ for the matching process
        
        If a substring of the two words is matched the pronunciation is added to the graph data structure by addPron(match, start_index, myWord[start_index], end_index, myWord[end_index]).
    """
    def partialMatch(self,myWord,dict_entry,pron):               
        str1 = myWord
        str2 = dict_entry
        flag = False
        str1Len = len(str1)
        str2Len = len(str2)
        if(str1Len < str2Len):
            flag = True
            temp = str1
            str1 = str2
            str2 = temp
    
        steps = str1Len - str2Len
        range1 = range(steps+1)
        range2 = range(len(str2))
        
        for i in range1:
            match = ""
            matchLen = 0
            for j in range2:
                if (str1[i+j] == str2[j]):
                    if(flag):
                        x = 2*(i+j)
                    else:
                        x = 2*j
                    y = x+2
                    match += pron[x:y]
                    matchLen += 2
                else:
                    if (matchLen >= 4):
                        if(flag):
                            start_index = j-matchLen/2 
                            end_index = j-1
                        else:
                            start_index = j-matchLen/2 + i
                            end_index = j-1+i
                        self.addPron(match, start_index, end_index)
    
                    match = ""
                    matchLen = 0
                    
            if(len(match) >= 4):
                if(flag):
                    start_index = j-(len(match)/2-1)
                    end_index = j
                else:
                    start_index = j-(len(match)/2-1) +i
                    end_index = j+i
                self.addPron(match, start_index, end_index)
    
    
    def addPron(self,pron, start_index, end_index):
        """
        Adds the pronunciation to the lattice data structure
        """
        
        #creation of the source node
        start_pron = pron[:2]  
        v1 = self.isNode(start_index,start_pron)
        if(v1 == False):
            v1 = self.addNode(start_index,start_pron)
    
    
        #creation of destination node
        end_pron = pron[-2:]
        v2 = self.isNode(end_index, end_pron)
        if(v2 == False):
            v2 = self.addNode(end_index,end_pron)
        
        
        #creation of edge connecting the two nodes
        edge_pron = pron[2:-2]
        edge = self.findEdge(v1,v2)
        if(edge == False):
            self.addEdge(v1,v2,edge_pron)
        else:
            self.g.es[edge]['freq'] += 1 
    
    
    def isNode(self,ind,pronun):
        '''
        SEARCH FOR A NODE IN THE LATTICE STRUCTURE
        IN_PARAMETERS:
        OUT: the index of the node
        '''
        
        seq = self.g.vs.select(index=ind,pron=pronun)
        
        if(not seq):
            return False
        else:
            return seq[0].index
            
    
    
    
    def addNode(self,ind,pronun):
        """
        ADD A NODE IN THE LATTICE STRCTURE 
        """
        self.g.add_vertex(index=ind, pron=pronun)
        return self.isNode(ind,pronun)
    
    
    def findEdge(self,v1, v2):
        """
        SEARCH FOR AN EDGE IN THE LATTICE STRUCTURE
        """
        es = self.g.es.select(_between = ([v1],[v2]))
        if(not es):
            return False
        else:
            for e in es:
                return e.index
    
    
    def addEdge(self,n_start,n_final,pronun):
        """
        ADD AN EDGE BETWEEN TWO NODES
        """
        self.g.add_edge(n_start, n_final, pron = pronun, freq = 1)
    
    def heuristic1(self):
        pass
    
    def getPronun(self,input_word):
        myDict = self.loadDict('beep.aligned')
        myDictKeys = myDict.keys()
        #sDict = ["string","submarine","subsist", "sonata", 'substring', 'start','sky','stolen']
        #sDict = [word.upper() for word in sDict]
    
        str1 = input_word
        str1 = '#' + str1 + '#'
        
        for dict_entry in myDictKeys:
            str2 = dict_entry    
            pron = "##" + myDict[dict_entry] + "##"
            str2 = '#' + str2 + '#'
    
            self.partialMatch(str1, str2, pron)
        
        start_node = self.g.vs.select(index = 0)
        end_node = self.g.vs.select(index = len(input_word)+1)
        
        #self.g.to_directed(False)

        vls = self.g.get_shortest_paths(start_node[0].index,end_node,mode=1,output="vpath")
        els = self.g.get_shortest_paths(start_node[0].index,end_node,mode=1,output="epath")
        
        
        print "Number of paths: " + str(len(vls))
        print vls
        vls = vls[0]
        els = els[0]
        
        result = ""
        
        x = 0
        y = 0
        for i in range(len(vls)+len(els)):
            if (i%2 == 0):
                result = result + self.g.vs[vls[x]]['pron']
                x = x + 1
            else:
                result = result + self.g.es[els[y]] ['pron']
                y = y + 1
        
        return result
            
    def leaveOneOutValidation(self,input_word):
        myDict = self.loadDict('beep.aligned')
        myDictKeys = myDict.keys()
        #sDict = ["string","submarine","subsist", "sonata", 'substring', 'start','sky','stolen']
        #sDict = [word.upper() for word in sDict]
    
        str1 = input_word
        str1 = '#' + str1 + '#'

        for dict_entry in myDictKeys:
            if(dict_entry != input_word):
                str2 = dict_entry    
                pron = "##" + myDict[dict_entry] + "##"
                str2 = '#' + str2 + '#'
    
                self.partialMatch(str1, str2, pron)
        
        start_node = self.g.vs.select(index = 0)
        end_node = self.g.vs.select(index = len(input_word)+1)
                 
        #vls = self.g.get_shortest_paths(start_node[0].index,end_node,mode=1,output="vpath")
        #els = self.g.get_shortest_paths(start_node[0].index,end_node,mode=1,output="epath")
        
        vls2 = self.g.get_all_shortest_paths(start_node[0].index,end_node,mode=1)
        
        #print "Paths: " + str(vls2)
        return self.computePronHeuristic1(vls2)
        #print "Path: " + str(vls)
        #vls = vls[0]
        #els = els[0]
        
        #result = ""
        
        #x = 0
        #y = 0
        #for i in range(len(vls)+len(els)):
            #if (i%2 == 0):
                #result = result + self.g.vs[vls[x]]['pron']
                #x = x + 1
            #else:
                #result = result + self.g.es[els[y]] ['pron']
                #y = y + 1
        
        #return result

    """
        Multiply heuristic
    """ 
    def computePronHeuristic1(self, lsPaths):
        
        dictPron = {}
        lsPron = []
        for path in lsPaths:
            pron = ""
            freq = 0
            lsIndex = []
            for vi in range(len(path)):
                v1 = vi
                v2 = vi+1
                if(v2 < len(path)):
                    pron = pron + self.g.vs[path[v1]]['pron'] + self.g.es[self.findEdge(path[v1], path[v2])]['pron']
                    freq = freq + self.g.es[self.findEdge(path[v1], path[v2])]['freq']
                    lsIndex.append(self.g.vs[path[v1]]['index'])
                    lsIndex.append(self.g.vs[path[v2]]['index']) 
                else:
                    pron += self.g.vs[path[v1]]['pron']
                    lsIndex.append(self.g.vs[path[v1]]['index'])
                    
            pron = pron[2:-2]
            if(dictPron.has_key(pron)):
                dictPron[pron] += freq
            else:
                dictPron[pron] = freq
            
            #lsPron.append(pron[2:-2])
            #lsPron.append(freq)
            #lsPron.append(lsIndex)
        
        maxFreq = 0
        maxPron = ""
        
        for k in dictPron.keys():
            if(dictPron[k] > maxFreq):
                maxFreq = dictPron[k]
                maxPron = k
                
        return maxPron  
        
        

def testAppNCrossVal():
    """
    Test for 100 words with full dictionary. Very slow.
    """
    #input_word = "LONGSHOREMAN"
    #PbA().getPronun(input_word)
    
    myDict = open('beep.aligned')
    wordDict = {}
    for line in myDict:
        key = line.split()[0]
        value = line.split()[1]
        wordDict[key] = value

    keys = wordDict.keys()
    
    err = 0
    for i in range(500):
        randIndex = random.randint(0,198632)
        input_word = keys[randIndex]
        print str(i) + ": " + input_word 
        r = PbA().leaveOneOutValidation(input_word)
        if r !=  wordDict[input_word]:
            err += 1
            print "Wrong pron of: " + input_word + " generated: " + r + " correct: " + wordDict[input_word] 
        print "Error: " + str(err)


def testApp():
    """
    Test for one word with full dictionary.
    """
    input_word = "NECROMANCY"
    
    #print "Desired pronunciation: " + "_LOHNG_-SH_-AO_-_-_MAX_N"
    print "Generated pronunciation: " + PbA().leaveOneOutValidation(input_word)[2:-2]
    print ""
        
if __name__ == "__main__":
    cProfile.run('testAppNCrossVal()')