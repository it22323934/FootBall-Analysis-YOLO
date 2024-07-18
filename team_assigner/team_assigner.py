from sklearn.cluster import KMeans

class TeamAssigner:
    
    def __init__(self):
        self.team_colors={}
        self.player_teams_dict={}
    
    def get_clustering_model(self,image):
        #Reshape image into 2D array
        image_2d=image.reshape(-1,3)
        
        #perfrom k-means with 2 clusters
        kmeans=KMeans(n_clusters=2,init="k-means++",n_init=10)
        kmeans.fit(image_2d)
        
        return kmeans
    
    def get_player_color(self,frame,bbox):
        image=frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]
        #Top half of the image
        top_half_image=image[0:int(image.shape[0]/2),:]
        
        #Get the clustering model
        kmeans=self.get_clustering_model(top_half_image)
        
        #Get the cluster labels for each pixel
        labels=kmeans.labels_
        
        #Reshape the labels to image shape
        clustered_image=labels.reshape(top_half_image.shape[0],top_half_image.shape[1])
        
        #Get the player cluster
        corner_cluster=[clustered_image[0,0],clustered_image[0,-1],clustered_image[-1,0],clustered_image[-1,-1]]
        non_player_cluster=max(set(corner_cluster),key=corner_cluster.count)
        player_cluster=1-non_player_cluster
        
        player_color=kmeans.cluster_centers_[player_cluster]
        
        return player_color
        
    def assign_teams_color(self,frame,player_detections):
        player_colors=[]
        for _,player_detection in player_detections.items():
            bbox=player_detection["bbox"]
            player_color=self.get_player_color(frame,bbox)
            player_colors.append(player_color)
            
        kmeans=KMeans(n_clusters=2,init="k-means++",n_init=10)
        kmeans.fit(player_colors)
        
        self.kmeans=kmeans
        
        #Assign color to each team
        self.team_colors[1]=kmeans.cluster_centers_[0]
        self.team_colors[2]=kmeans.cluster_centers_[1]
        
    def get_player_team(self,frame,player_bbox,player_id):
        if player_id in self.player_teams_dict:
            return self.player_teams_dict[player_id]
        
        player_color=self.get_player_color(frame,player_bbox)
        
        team_id=self.kmeans.predict(player_color.reshape(1,-1))[0]
        team_id+=1
        
        if player_id==102:
            team_id=1
            
        if player_id==197:
            team_id=2
            
        
        self.player_teams_dict[player_id]=team_id
        
        return team_id