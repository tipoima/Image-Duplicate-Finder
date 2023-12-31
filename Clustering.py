

class Clustering:
    def __init__(self,images,RGBmode=False,threshold=4):
        self.imgCount=len(images.index)
        self.images=images['path'].to_list()


        if RGBmode:
            self.hashes=images['rgbHash'].to_list()
            self.hashes=list(map(int, self.hashes))
        else:
            self.hashes=images['gsHash'].to_list()
            self.hashes=list(map(int, self.hashes))

        self.unionFind=[i for i in range(self.imgCount)]
        self.ranks=[0 for _ in range(self.imgCount)]
        
        self.threshold=threshold
        
        
    def getClusters(self):
        self.__cluster()
        clusters=dict()
        for i in range(self.imgCount):
            parent=self.__find(i)
            if clusters.get(parent) is None:
                clusters[parent]=[self.images[i]]
            else:
                clusters[parent].append(self.images[i])
        return clusters
         
        
    def __find(self,x):
        if self.unionFind[x]==x:
            return x
        else:
            self.unionFind[x]=self.__find(self.unionFind[x])
            return self.unionFind[x]

    def __union(self,x,y):
        if self.__find(x)==self.__find(y):
            return
        if self.ranks[x]==self.ranks[y]:
            self.unionFind[y]=x
            self.ranks[x]+=1
        elif self.ranks[x]>self.ranks[y]:
            self.unionFind[y]=x
        else:
            self.unionFind[x]=y
        return           
    
    def __hammingDistance(self,hash1:int,hash2:int):
        #assert len(bin(hash1))==len(bin(hash2)),"Hash lengths not equal"
        return (hash1^hash2).bit_count()
    
    def __cluster(self):
        for i in range(self.imgCount):
            self.__nearestNeighbour(i)
    
    def __nearestNeighbour(self,idx):
        dists=[(self.__hammingDistance(self.hashes[i],self.hashes[idx]),i) for i in range(self.imgCount)]

        for dist in dists:
            if dist[0]<self.threshold:
                self.__union(dist[1],idx)


if __name__=="__main__":
    import json
    import pandas as pd
    from PIL import Image
    from ImageCollector import ImageCollector
    images=ImageCollector.getImages(r"D:\Downloads",True)
    clusterGenerator=Clustering(images)
    clusters=clusterGenerator.getClusters()
    clusters={k: v for k,v in clusters.items() if len(v)>1}
    #json.dump(clusters,open("mega_dump.json",'w'))