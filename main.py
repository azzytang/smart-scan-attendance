
from kivy.config import Config

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '650')
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import numpy as np
import face_recognition
import json
import requests
import re
from pyzbar import pyzbar
import cv2
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.app import App


Builder.load_string("""
<MenuScreen>:
    RelativeLayout:
        Label: 
            text: 'SmartScan Attendance'
            font_size: 50
            pos_hint: {'center_x': 0.5, 'center_y': 0.9}
        Label:
            text: 'Scan ID and Face Here:'
            font_size: 30
            color: '#FFFFFF' 
            pos_hint: {'center_x': 0.5, 'center_y': 0.7}
                    
        Button:
            text: 'add student'
            on_press: root.manager.current = 'settings'
            size: 200, 120
            size_hint: None, None
            pos_hint: {'center_x': 0.5, 'center_y': 0.2}
        Image: 
            source: 'white_corner.png'
            pos_hint: {'center_x': 0.148, 'center_y': 0.622}
        Image: 
            source: 'white_corner2.png'
            pos_hint: {'center_x': 0.148, 'center_y': 0.375}
        Image: 
            source: 'white_corner3.png'
            pos_hint: {'center_x': 0.852, 'center_y': 0.375}
        Image: 
            source: 'white_corner4.png'
            pos_hint: {'center_x': 0.852, 'center_y': 0.622}
                    
      
<SettingsScreen>:
    RelativeLayout:
        
        Button:
            text: 'Back'
            size: 200, 120
            size_hint: None, None
            pos_hint: {'center_x': 0.5, 'center_y': 0.1}
            on_press: root.manager.current = 'menu'
        
""")

ids = []


class MenuScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


firebase_link = ""

with open("firebase_link.txt") as file:
    file.readline()


class ScanApp(App):

    def build(self):
        self.sm = ScreenManager()

        self.students = {}
        self.ariana = face_recognition.load_image_file(
            "data/ariana_grande_photo_jon_kopaloff_getty_images_465687098.jpg")
        self.ariana_face_encoding = face_recognition.face_encodings(self.ariana)[
            0]

        self.known_face_encodings = [
            self.ariana_face_encoding
        ]
        self.known_face_names = [
            "Ariana Grande"

        ]

        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.scanned_text = Label(text="", font_size=20, color='87cc74', pos_hint={
                                  'center_x': 0.5, 'center_y': 0.65})
        self.image = Image(size_hint=(None, None), size=(
            550, 400), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.image_settings = Image(size_hint=(None, None), size=(
            550, 400), pos_hint={'center_x': 0.5, 'center_y': 0.8})

        self.name_input = TextInput(text="Name", font_size=35, multiline=False, size_hint=(
            None, None), size=(300, 100), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.id_input = TextInput(text="ID", font_size=35, multiline=False, size_hint=(
            None, None), size=(300, 100), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        submit_button = Button(text="Submit", on_press=self.new_student, size=(
            200, 120), size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.25})
        settings_screen = SettingsScreen(name='settings')
        menu_screen = MenuScreen(name='menu')
        menu_screen.add_widget(self.image)
        menu_screen.add_widget(self.scanned_text)
        settings_screen.add_widget(submit_button)
        settings_screen.add_widget(self.name_input)
        settings_screen.add_widget(self.id_input)
        settings_screen.add_widget(self.image_settings)

        self.sm.add_widget(menu_screen)
        self.sm.add_widget(settings_screen)
        self.capture = cv2.VideoCapture(0)

        Clock.schedule_interval(self.load_video, 1/60)

        return self.sm

    def detect_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        self.face_locations = face_recognition.face_locations(small_frame)
        self.face_encodings = face_recognition.face_encodings(
            small_frame, self.face_locations)
        self.detected_names = []
        self.face_names = []
        for face_encoding in self.face_encodings:
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

            self.face_names.append(name)
            self.detected_names.append(name)

        self.process_this_frame = not self.process_this_frame

        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35),
                          (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)
        return frame

    def load_video(self, *args):
        ret, self.frame = self.capture.read()
        if self.sm.current == 'menu':
            self.frame = self.detect_faces(self.frame)
            self.frame = self.decode(self.frame)

        buffer = cv2.flip(self.frame, 0).tobytes()
        texture1 = Texture.create(
            size=(self.frame.shape[1], self.frame.shape[0]), colorfmt="bgr")
        texture1.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
        if self.sm.current == 'menu':
            self.image.texture = texture1
        else:
            self.image_settings.texture = texture1

    def decode(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(gray)
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            barcode_info = barcode.data.decode('utf-8')
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, barcode_info, (x + 6, y - 6),
                        font, 2.0, (255, 255, 255), 1)
            if barcode_info not in ids and len(re.findall("[0-9]{6}", barcode_info)) == 1:
                try:
                    if self.students[barcode_info] in self.detected_names:
                        headers = {
                            "Content-Type": "application/json"
                        }
                        data = barcode_info
                        json_data = json.dumps(data)
                        response = requests.post(
                            firebase_link, headers=headers, data=json_data)
                        print(response.json())

                        ids.append(barcode_info)
                        print(ids)
                        self.scanned_text.text = "ID Scanned!"
                        Clock.schedule_once(self.remove_scanned, 1)
                except:
                    pass

        return image

    def remove_scanned(self, *args):
        self.scanned_text.text = ""

    def new_student(self, instance):
        id = self.id_input.text
        name = self.name_input.text
        self.students[id] = name
        cv2.imwrite('data/image.png', self.frame)

        student = face_recognition.load_image_file('data/image.png')
        student_face_encoding = face_recognition.face_encodings(student)[0]
        self.known_face_encodings.append(student_face_encoding)
        self.known_face_names.append(name)


if __name__ == '__main__':
    ScanApp().run()
