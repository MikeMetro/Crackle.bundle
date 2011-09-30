import re

TITLE = 'Crackle'

ART = 'art-default.jpg'
ICON = 'icon-default.png'

URL_BASE_TITLES = 'http://www.crackle.com/chromewebapp/ShowList.aspx?'
URL_PARAMS = 'cl=%s&fb=%s'
URL_PARAMS_INNER = '&o=%s&fa=%s&fs=&fx=&fab=&fg=%s&fry='
URL_CHANNEL_DETAILS = 'http://www.crackle.com/chromewebapp/WatchShow.aspx?cid=%s&pid=%s&id=%s'
URL_TITLE_DETAILS = 'http://www.crackle.com/chromewebapp/NowPlaying.aspx?mediaId=%s&id=%s'
URL_VIDEO_BASE = 'http://cdn1.crackle.com'

###################################################################################################

def Start():
  Plugin.AddPrefixHandler('/video/crackle', MainMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup('List', viewMode = 'List', mediaType = 'items')
  Plugin.AddViewGroup('InfoList', viewMode = 'InfoList', mediaType = 'items')

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
  HTTP.CacheTime = CACHE_1DAY

###################################################################################################

def MainMenu():
  oc = ObjectContainer()

  oc.add(DirectoryObject(key = Callback(Genres, title = 'Movies', category = '82'), title = 'Movies'))
  oc.add(DirectoryObject(key = Callback(Genres, title = 'Television', category = '114'), title = 'Television'))
  oc.add(DirectoryObject(key = Callback(Genres, title = 'Original', category = '46'), title = 'Original'))
  oc.add(DirectoryObject(key = Callback(Genres, title = 'Collections', category = '586'), title = 'Collections'))

  return oc

###################################################################################################

def Genres(title, category):
  oc = ObjectContainer(title2 = title)

  oc.add(DirectoryObject(key = Callback(ListChannels, title = 'All Genres', category = category, genre = ''), title = 'All Genres'))
  oc.add(DirectoryObject(key = Callback(ListChannels, title = 'Action', category = category, genre = 'action'), title = 'Action'))
  oc.add(DirectoryObject(key = Callback(ListChannels, title = 'Comedy', category = category, genre = 'comedy'), title = 'Comedy'))
  oc.add(DirectoryObject(key = Callback(ListChannels, title = 'Crime', category = category, genre = 'crime'), title = 'Crime'))
  oc.add(DirectoryObject(key = Callback(ListChannels, title = 'Thriller', category = category, genre = 'thriller'), title = 'Thriller'))
  oc.add(DirectoryObject(key = Callback(ListChannels, title = 'Horror', category = category, genre = 'horror'), title = 'Horror'))
  oc.add(DirectoryObject(key = Callback(ListChannels, title = 'Sci-Fi', category = category, genre = 'sci-fi'), title = 'Sci-Fi'))

  return oc

###################################################################################################

def ListChannels(title, category, genre, filter ='7', type = 'a'):
  oc = ObjectContainer(title2 = title)

  url_params_inner = URL_PARAMS_INNER % (filter, category, genre)
  url_params = URL_PARAMS %  (String.Quote(url_params_inner), type)
  url = URL_BASE_TITLES + url_params
  page = HTML.ElementFromURL(url)
  
  page_index = 0
  while(True):
    page = HTML.ElementFromURL(url + '&&usePageCookie=false&p=' + str(page_index))
  
    for item in page.xpath("//ul[@class='showsDetailed']/li"):
      item_title = ''.join(item.xpath(".//div[@class='title']//text()")).strip()
      thumb = item.xpath(".//img")[0].get('src')

      link_details = item.xpath(".//a")[0].get('onclick')
      link_details = link_details[link_details.find('('):link_details.rfind(')')].split(',')
      channel_id = link_details[1].strip()
      playlist_id = link_details[2].strip()
      movie_id = link_details[4].strip()

      channel_url = URL_CHANNEL_DETAILS % (channel_id, playlist_id, movie_id)

      oc.add(DirectoryObject(key = Callback(ListTitles, title = item_title, channel_url = channel_url), title = item_title, thumb = thumb))

    page_index = page_index + 1
    page_index_text = page.xpath("//div[@id='pagerBottom']/span[@class='text']/text()")
    if len(page_index_text) == 0:
      break
    
    page_index_text = page_index_text[0]
    max_page = int(re.match("Page [0-9]+ of (?P<max>[0-9]+)", page_index_text).groupdict()['max'])
    if page_index == max_page:
      break

  if len(oc) == 0:
    return MessageContainer("Error", "No titles were found!")
    
  return oc

###################################################################################################

def ListTitles(title, channel_url):
  oc = ObjectContainer(title2 = title, view_group = 'InfoList')

  page_index = 0
  while(True):
    page = HTML.ElementFromURL(channel_url + '&p=' + str(page_index))
    for item in page.xpath("//div[@class='episodes']//li"):

      thumb_link = item.xpath(".//img[@id='imgMediaThumbnail']")[0].get('src')
      video_path = thumb_link[thumb_link.find('.com') + 4: thumb_link.rfind('_') + 1]
      video_url = URL_VIDEO_BASE + video_path + "%s" + '.mp4'

      item_id_text = item.get('onclick')
      media_id = re.match(".*\((?P<media_id>[0-9]+),.*", item_id_text).groupdict()['media_id']
      channel_id = page.xpath("//input[@id='channelId']")[0].get('value')
      item_url = URL_TITLE_DETAILS % (media_id, channel_id)

      item_page = HTML.ElementFromURL(item_url)

      item_title = ''.join(item_page.xpath(".//h3[@id='mediaTitle']/text()")).strip()
      thumb = item_page.xpath(".//div[@class='thumbImg']//img")[0].get('src')
        
      # [Optional]
      content_rating = None
      try: content_rating = item_page.xpath("//b[contains(text(), Rating)]/text()")[0].split(':')[1].strip()
      except: pass

      # [Optional]
      directors = []
      try: directors = item_page.xpath("//h3[contains(text(), 'Director')]/following-sibling::div/text()")[0].split(',')
      except: pass
      directors = [ dir.strip for dir in directors ]
        
      summary_specific = ''.join(item_page.xpath(".//div[@class='showDetails']//div[@id='mediaDesc']/text()")).strip()
      summary_basic = ''.join(item_page.xpath(".//div[@class='showDetailsMore']//div[@class='synopsis']/text()")).strip()
      summary = "%s\n\n%s" % (summary_specific, summary_basic)
      
      oc.add(VideoClipObject(
        rating_key = item_url,
        title = item_title,
        summary = summary,
        thumb = thumb,
        directors = directors,
        content_rating = content_rating,
        items = [
          MediaObject(
            video_codec = VideoCodec.H264,
            audio_codec = AudioCodec.AAC,
            video_resolution = 480,
            protocols = [Protocol.HTTPMP4Video],
            parts = [PartObject(key = video_url % "480p")]
          ),
          MediaObject(
            video_codec = VideoCodec.H264,
            audio_codec = AudioCodec.AAC,
            video_resolution = 360,
            protocols = [Protocol.HTTPMP4Video],
            parts = [PartObject(key = video_url % "360p")]
          )
        ]
      ))

    page_index = page_index + 1
    next_page = page.xpath("//div[contains(@class, 'right-next-button')]")
    if len(next_page) == 0:
      break

  return oc