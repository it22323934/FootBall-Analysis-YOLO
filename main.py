from util.video_utils import read_video, save_video
from trackers import Tracker
import cv2
from team_assigner import TeamAssigner
import numpy as np
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
def  main():
    #Read Video
    video_path = 'input_video/08fd33_4.mp4'
    video_Frames=read_video(video_path)
    print(len(video_Frames))
    
    #Initialize Tracker
    tracker=Tracker('models/best.pt')
    tracks=tracker.get_object_tracks(video_Frames, read_from_stub=True,stub_path='stubs/track_stubs.pkl')
    
    # Get object positions
    tracker.add_position_to_tracks(tracks)
    
    #camera movement estimation
    camera_movement_estimator=CameraMovementEstimator(video_Frames[0])
    camera_move_per_frame=camera_movement_estimator.get_camera_movement(video_Frames,read_from_stub=True,stub_path='stubs/camera_movement_stubs.pkl')
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks,camera_move_per_frame)
    
    
    #view Transformer
    view_transformer=ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)
    
    #Interpolate ball positions
    tracks["ball"]=tracker.interpolate_ball_positions(tracks["ball"])
    
    #Speed and Distance Estimation
    speed_and_distance_estimator=SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)
    
    #Assign Player Teams
    team_assigner=TeamAssigner()
    team_assigner.assign_teams_color(video_Frames[0],tracks["players"][0])
    
    for frame_num,player_track in enumerate(tracks["players"]):
        for player_id,track in player_track.items():
            team=team_assigner.get_player_team(video_Frames[frame_num],track["bbox"],player_id)
            tracks["players"][frame_num][player_id]["team"]=team
            tracks["players"][frame_num][player_id]["team_color"]=team_assigner.team_colors[team]
    

    #Assign Ball to Players
    player_assigner=PlayerBallAssigner()
    team_ball_control=[]
    for frame_num,player_track in enumerate(tracks["players"]):
        ball_bbox=tracks["ball"][frame_num][1]["bbox"]
        assigned_player=player_assigner.assign_player_ball(player_track,ball_bbox)
        
        if assigned_player !=-1:
            tracks["players"][frame_num][assigned_player]["has_ball"]=True
            team_ball_control.append(tracks["players"][frame_num][assigned_player]["team"])
        else:
            team_ball_control.append(team_ball_control[-1])
    
    team_ball_control=np.array(team_ball_control)     
    #Draw ouput
    ##Draw object tracks on the frames
    output_video_frames=tracker.draw_annotations(video_Frames,tracks,team_ball_control)
    
    #Draw Camer movement
    output_video_frames=camera_movement_estimator.draw_camera_movement(output_video_frames,camera_move_per_frame)
    
    #Draw Speed and Distance
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames,tracks)
    
    #Save Video
    save_video(output_video_frames, 'output_video/output.avi')
    
if __name__ == "__main__":
    main()