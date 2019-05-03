# coding=utf-8

from random import randint


class pyperclip():

    clip_file = open("clip", mode="w")
    clip_file.close()

    @staticmethod
    def copy(value):
        clip_file = open("clip", mode="w")
        clip_file.write(value)
        clip_file.close()


    @staticmethod
    def paste():
        clip_file = open("clip", "r")
        clip = clip_file.read()
        return clip



pyperclip.change_clip()
print(pyperclip.paste())
