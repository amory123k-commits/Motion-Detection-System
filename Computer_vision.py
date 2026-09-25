import cv2 
import os
import numpy as np
import pandas as pd
from collections import deque
from lxml import objectify
import _pickle as pickle
import psycopg2
import pymongo
from sqlalchemy import create_engine

data_records=[]
frame_id=0
#1- read the xml file
xml=objectify.parse('config.xml')
root=xml.getroot()
threshold_value=int(root.gray_threshold)
name_vid=str(root.video_source)
min_area=int(root.min_area)



#2-  detect the path video and read the video
path_video=os.path.join('.','video',name_vid)
video=cv2.VideoCapture(path_video)

ret,first_frame=video.read()
if ret:
    back_ground = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    back_ground=cv2.GaussianBlur(back_ground,(21,21),0)
    with open('myfile.pkl','wb') as file:
        pickle.dump(back_ground,file)


scores_window = deque(maxlen=10)
while True:
    Status='NORMAL'
    ret,frame=video.read()

    if not ret:
        break
    frame_id=1+frame_id
    
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    diff=cv2.absdiff(back_ground,blur_frame)
    retval, dst=cv2.threshold(diff,threshold_value,255,cv2.THRESH_BINARY)

    motion_score=np.sum(dst==255)
    scores_window.append(motion_score)
    avg_score=sum(scores_window)/len(scores_window)
    if avg_score>min_area:
        Status='ALERT'
    contours, hierarchy=cv2.findContours(dst,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
       
        if cv2.contourArea(contour)> min_area:
            x,y,w,h=cv2.boundingRect(contour)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        


    data_records.append({
        'Frame_id':frame_id,
        'Motion_Score':int(motion_score),
        'Avg_Score':int(avg_score),
        'Status':Status
        
        })

    
video.release()
df=pd.DataFrame(data_records)
print('size before:')
print(df.info())
df['Frame_id']=df['Frame_id'].astype('int32')
df['Motion_Score']=df['Motion_Score'].astype('int32')
df['Avg_Score']=df['Avg_Score'].astype('int32')
df['Status']=df['Status'].astype('category')
print('size After')
print(df.info())    

print('connecting now sql')
engine=create_engine('postgresql+psycopg2://ammar:123@localhost:5432/security_db')

df_alerts=df[df['Status']=='ALERT']
if not df_alerts.empty:
    df_alerts.to_sql('security_alerts',engine,if_exists='replace',index=False)
    print(f"[SUCCESS] {len(df_alerts)},security alerts inserted into PostgreSQL.")
else:
    print('No alerts')

print('connecting now nosql')
mongo_client=pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db=mongo_client['security_analytics']
mongo_collection=mongo_db['frame_data']
mongo_collection.delete_many({})
mongo_data=df.to_dict(orient='records')

mongo_collection.insert_many(mongo_data)

print('hdf5')

hdf_path='motion_archive.h5'
df.to_hdf(hdf_path,key='motion_data',mode='w',format='table')
print('Done')