TITLE = 'Crackle'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

URL_BASE_TITLES = 'http://www.crackle.com/chromewebapp/ShowList.aspx?'
URL_PARAMS = 'cl=%s&fb=%s'
URL_PARAMS_INNER = '&o=%s&fa=%s&fs=&fx=&fab=&fg=%s&fry='
URL_VIDEO_DETAILS = 'http://www.crackle.com/chromewebapp/WatchShow.aspx?cid=%s&pid=%s&id=%s'
URL_VIDEO_BASE = 'http://cdn1.crackle.com'

###################################################################################################

def Start():
  Plugin.AddPrefixHandler('/video/crackle', MainMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup('List', viewMode = 'List', mediaType = 'items')
  Plugin.AddViewGroup('InfoList', viewMode = 'InfoList', mediaType = 'items')

  # Set the default ObjectContainer attributes
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'InfoList'
  ObjectContainer.art = R(ART)

  # Default icons for DirectoryItem and WebVideoItem in case there isn't an image
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  # Set the default cache time
  HTTP.CacheTime = CACHE_1HOUR

###################################################################################################

def MainMenu():
  oc = ObjectContainer(view_group = 'List')

  oc.add(DirectoryObject(key = Callback(Genres, title = 'Movies', category = '82'), title = 'Movies'))
  oc.add(DirectoryObject(key = Callback(Genres, title = 'Television', category = '114'), title = 'Television'))
  oc.add(DirectoryObject(key = Callback(Genres, title = 'Original', category = '46'), title = 'Original'))
  oc.add(DirectoryObject(key = Callback(Genres, title = 'Collections', category = '586'), title = 'Collections'))

  return oc

###################################################################################################

def Genres(title, category):
  oc = ObjectContainer(view_group = 'List')

  oc.add(DirectoryObject(key = Callback(ListTitles, title = 'All Genres', category = category, genre = ''), title = 'All Genres'))
  oc.add(DirectoryObject(key = Callback(ListTitles, title = 'Action', category = category, genre = 'action'), title = 'Action'))
  oc.add(DirectoryObject(key = Callback(ListTitles, title = 'Comedy', category = category, genre = 'comedy'), title = 'Comedy'))
  oc.add(DirectoryObject(key = Callback(ListTitles, title = 'Crime', category = category, genre = 'crime'), title = 'Crime'))
  oc.add(DirectoryObject(key = Callback(ListTitles, title = 'Thriller', category = category, genre = 'thriller'), title = 'Thriller'))
  oc.add(DirectoryObject(key = Callback(ListTitles, title = 'Horror', category = category, genre = 'horror'), title = 'Horror'))
  oc.add(DirectoryObject(key = Callback(ListTitles, title = 'Sci-Fi', category = category, genre = 'sci-fi'), title = 'Sci-Fi'))

  return oc

###################################################################################################

def ListTitles(title, category, genre, filter ='7', type = 'f'):
  oc = ObjectContainer(view_group = 'List')

  url_params_inner = URL_PARAMS_INNER % (filter, category, genre)
  url_params = URL_PARAMS %  (String.Quote(url_params_inner), type)
  url = URL_BASE_TITLES + url_params
  page = HTML.ElementFromURL(url)
  
  for item in page.xpath("//ul[@class='showsDetailed']/li"):
    item_title = ''.join(item.xpath(".//div[@class='title']//text()")).strip()
    thumb = item.xpath(".//img")[0].get('src')

    link_details = item.xpath(".//a")[0].get('onclick')
    link_details = link_details[link_details.find('('):link_details.rfind(')')].split(',')
    channel_id = link_details[1].strip()
    playlist_id = link_details[2].strip()
    movie_id = link_details[4].strip()

    title_url = URL_VIDEO_DETAILS % (channel_id, playlist_id, movie_id)

    oc.add(VideoClipObject(
      url = title_url,
      title = item_title,
      thumb = thumb,
      items = [
        MediaObject(
          video_codec = VideoCodec.H264,
          audio_codec = AudioCodec.AAC,
          video_resolution = 480,
          protocols = [Protocol.HTTPMP4Video],
          parts = [PartObject(key=Callback(PlayVideo, url = title_url, res = '480p'))]
        ),
        MediaObject(
          video_codec = VideoCodec.H264,
          audio_codec = AudioCodec.AAC,
          video_resolution = 360,
          protocols = [Protocol.HTTPMP4Video],
          parts = [PartObject(key=Callback(PlayVideo, url = title_url, res = '360p'))]
        )
      ]
    ))

  return oc

###################################################################################################

def PlayVideo(url, res):

  page = HTML.ElementFromURL(url)
  thumb = page.xpath("//img[@id='imgMediaThumbnail']")[0].get('src')

  video_path = thumb[thumb.find('.com') + 4: thumb.rfind('_') + 1]
  video_url = URL_VIDEO_BASE + video_path + res + '.mp4'
  return Redirect(video_url)