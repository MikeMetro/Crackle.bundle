import re

TITLE = 'Jerry Seinfeld'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.jerryseinfeld.com'

###################################################################################################

def Start():
  Plugin.AddPrefixHandler('/video/jerryseinfeld', MainMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup('List', viewMode = 'List', mediaType = 'items')

  # Set the default ObjectContainer attributes
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'List'
  ObjectContainer.art = R(ART)

  # Default icons for DirectoryObject and VideoClipObject in case there isn't an image
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  # Set the default cache time
  HTTP.CacheTime = CACHE_1HOUR

###################################################################################################

def MainMenu():
  oc = ObjectContainer()

  page_content = HTTP.Request(BASE_URL).content
  for video in re.finditer('data\("video", ([^\)]+?)\)', page_content):
    video_details = JSON.ObjectFromString(video.groups()[0])
    oc.add(VideoClipObject(
      url = BASE_URL,
      title = video_details['title'],
      thumb = video_details['jpg'],
      items = [
        MediaObject(
          video_codec = VideoCodec.H264,
          audio_codec = AudioCodec.AAC,
          protocols = [Protocol.HTTPMP4Video],
          parts = [PartObject(key = video_details['mp4'])]
        )
      ]
    ))

  return oc