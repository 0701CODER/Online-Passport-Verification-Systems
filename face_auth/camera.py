import cv2
import face_recognition
import numpy as np
from django.contrib.staticfiles import finders
from django.contrib.auth import login
from django.http import HttpResponseRedirect
# from .views import welcome
from django.shortcuts import render,redirect
from django.http import JsonResponse



# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def welcome(request,user):
    """
    It takes a request and a user, and sets the user's face_auth to True
    
    :param request: The request object
    :param user: The user object that was authenticated
    """
    user.face_auth = True
    user.save()


def gen_frames(request,user):
    """
    It takes a request and a user object, and returns a generator that yields a series of frames from
    the webcam
    
    :param request: The request object
    :param user: The user object
    """
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)

    # Load a sample picture and learn how to recognize it.
    img = finders.find(f'user_{user.username}/{user.username}.jpeg')
    user_image = face_recognition.load_image_file(img)
    user_face_encoding = face_recognition.face_encodings(user_image)[0]
    Auth = False
    i = 0


    # Create arrays of known face encodings and their names
    known_face_encodings = [
    user_face_encoding,
    ]
    known_face_names = [
        user.username,
    ]

    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
           
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                
                face_names.append(name)

                if name == user.username:
                    Auth = True
                    # return render(request,'welcome.html')

            # Display the results
            if Auth:
                welcome(request,user)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    camera.release()
    # welcome(request)
    # yield(1)



        
        
    