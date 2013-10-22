# Twitch.tv Plugin
# v0.1 by Marshall Thornton <marshallthornton@gmail.com>
# Code inspired by Justin.tv plugin by Trevor Cortez and John Roberts

####################################################################################################

from html_helper import strip_tags
import urllib

TWITCH_LIST_STREAMS     = 'https://api.twitch.tv/kraken/streams'
TWITCH_FEATURED_STREAMS = 'https://api.twitch.tv/kraken/streams/featured'
TWITCH_TOP_GAMES        = 'https://api.twitch.tv/kraken/games/top'
TWITCH_SEARCH_STREAMS   = 'https://api.twitch.tv/kraken/search/streams'
TWITCH_LIVE_PLAYER      = 'http://www-cdn.jtvnw.net/widgets/live_embed_player.swf?auto_play=true'
TWITCH_FOLLOWED_STREAMS = 'https://api.twitch.tv/kraken/users/%s/follows/channels'


PAGE_LIMIT              = 100
CACHE_INTERVAL          = 600
NAME                    = 'Twitch.tv'
ART                     = 'art-default.jpg'
ICON                    = 'icon-default.png'
SETTINGS  		= 'settings-hi.png'



####################################################################################################
def Start():
    Plugin.AddPrefixHandler("/video/twitchtv", VideoMainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "InfoList"
    DirectoryItem.thumb = R(ICON)
    PrefsItem.thumb = R(ICON)
    InputDirectoryItem.thumb = R(ICON)


def CreatePrefs():
  Prefs.Add(id='username', type='text', default='', label='Username')

def VideoMainMenu():
    dir = MediaContainer(noCache=True)
    dir.Append(Function(DirectoryItem(FeaturedStreamsMenu, title="Featured Streams", summary="Browse featured streams")))
    dir.Append(Function(DirectoryItem(GamesMenu, title="Games", summary="Browse live streams by game")))
    dir.Append(Function(DirectoryItem(FollowedMenu, title="Followed", summary="Live Followed Channels")))
    dir.Append(Function(InputDirectoryItem(SearchResults, title="Search", prompt="Search For A Stream", summary="Search for a stream")))
    dir.Append(PrefsItem(title="Preferences", subtitle="Set Username", thumb=R(SETTINGS)))
    return dir


def FollowedMenu(sender, page=None):
    
    dir = ObjectContainer(title2="Followed")
    url = TWITCH_FOLLOWED_STREAMS % Prefs['username'] 
    channel_arr = []
    
    followed = JSON.ObjectFromURL(url, cacheTime=CACHE_INTERVAL)
    for follow in followed['follows']:
        channel = follow['channel']
        ch_name = channel['name']
        channel_arr.append(ch_name)
        
    streams = JSON.ObjectFromURL(TWITCH_LIST_STREAMS+"?%s" % urllib.urlencode({'channel' : ','.join(channel_arr)}))
          
    
    for stream in streams['streams']:    
        subtitle = "%s\n%s Viewers" % (stream['game'], stream['viewers'])
        summary = strip_tags(stream['channel']['status'])
        streamUrl = stream['channel']['url']
        dir.add(VideoClipObject(url=streamUrl, title=stream['channel']['display_name'], summary=summary, source_title=subtitle, thumb=stream['preview']['large']))

    return dir

        

    
def FeaturedStreamsMenu(sender, page=None):
    dir = ObjectContainer(title2='Featured')
    #dir = MediaContainer(viewGroup="List", title2="Featured Streams")
    url  = "%s?limit=%s" % (TWITCH_FEATURED_STREAMS, PAGE_LIMIT)

    featured = JSON.ObjectFromURL(url, cacheTime=CACHE_INTERVAL)
   
    for stream in featured['featured']:
        subtitle = "%s\n%s Viewers" % (stream['stream']['game'], stream['stream']['viewers'])
        summary = strip_tags(stream['text'])
        #streamUrl = "%s&channel=%s" % (TWITCH_LIVE_PLAYER, stream['stream']['channel']['name'])
        streamUrl = stream['stream']['channel']['url']
        dir.add(VideoClipObject(url=streamUrl, title=stream['stream']['channel']['display_name'], summary=summary, source_title=subtitle, thumb=stream['stream']['preview']['large']))

    return dir


def GamesMenu(sender, page=0):
    dir = MediaContainer(viewGroup="List", title2="Top Games")
    url  = "%s?limit=%s&offset=%s" % (TWITCH_TOP_GAMES, PAGE_LIMIT, page*PAGE_LIMIT)

    games = JSON.ObjectFromURL(url, cacheTime=CACHE_INTERVAL)
   
    for game in games['top']:
        gameSummary = "%s Channels\n%s Viewers" % (game['channels'], game['viewers'])
        dir.Append(Function(DirectoryItem(ChannelMenu, title=game['game']['name'], thumb=game['game']['logo']['large'], summary=gameSummary), game=game['game']['name']))

    if(len(games['top']) == 100):
        dir.Append(Function(DirectoryItem(GamesMenu, title="More Games"), page=(page+1)))

    return dir


def ChannelMenu(sender, game=None):
    dir = ObjectContainer(title2=sender.itemTitle)

    url = "%s?game=%s&limit=%s" % (TWITCH_LIST_STREAMS, urllib.quote_plus(game), PAGE_LIMIT)

    streams = JSON.ObjectFromURL(url, cacheTime=CACHE_INTERVAL)

    for stream in streams['streams']:
        subtitle = " %s Viewers" % stream['viewers']
        streamURL = stream['channel']['url'] 
        dir.add(VideoClipObject(url=streamURL, title=stream['channel']['display_name'], summary=stream['channel']['status'], source_title=subtitle, thumb=stream['preview']['large']))

    return dir


def SearchResults(sender, query=None):
    dir = ObjectContainer()


    results = JSON.ObjectFromURL("%s?query=%s&limit=%s" % (TWITCH_SEARCH_STREAMS, urllib.quote_plus(query), PAGE_LIMIT), cacheTime=CACHE_INTERVAL)

    for stream in results['streams']:
        subtitle = "%s\n%s Viewers" % (stream['game'], stream['viewers'])
        streamURL = stream['channel']['url'] 
        dir.add(VideoClipObject(url=streamURL, title=stream['channel']['display_name'], summary=stream['channel']['status'], source_title=subtitle, thumb=stream['preview']['large']))
    if len(dir) > 0:
        return dir
    else:
        return MessageContainer("Not found", "No streams were found that match your query.")
