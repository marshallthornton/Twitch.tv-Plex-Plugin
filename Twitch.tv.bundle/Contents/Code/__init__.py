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

PAGE_LIMIT              = 100
CACHE_INTERVAL          = 600
NAME                    = 'Twitch.tv'
ART                     = 'art-default.jpg'
ICON                    = 'icon-default.png'


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


def VideoMainMenu():
    dir = MediaContainer(noCache=True)
    dir.Append(Function(DirectoryItem(FeaturedStreamsMenu, title="Featured Streams", summary="Browse featured streams")))
    dir.Append(Function(DirectoryItem(GamesMenu, title="Games", summary="Browse live streams by game")))
    dir.Append(Function(InputDirectoryItem(SearchResults, title="Search", prompt="Search For A Stream", summary="Search for a stream")))
    return dir


def FeaturedStreamsMenu(sender, page=None):
    dir = MediaContainer(viewGroup="List", title2="Featured Streams")
    url  = "%s?limit=%s" % (TWITCH_FEATURED_STREAMS, PAGE_LIMIT)

    featured = JSON.ObjectFromURL(url, cacheTime=CACHE_INTERVAL)
   
    for stream in featured['featured']:
        subtitle = "%s\n%s Viewers" % (stream['stream']['game'], stream['stream']['viewers'])
        summary = strip_tags(stream['text'])
        streamUrl = "%s&channel=%s" % (TWITCH_LIVE_PLAYER, stream['stream']['channel']['name'])
        dir.Append(WebVideoItem(streamUrl, title=stream['stream']['channel']['display_name'], subtitle=subtitle, summary=summary, thumb=stream['stream']['preview']))

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
    dir = MediaContainer(title2=sender.itemTitle)
    url = "%s?game=%s&limit=%s" % (TWITCH_LIST_STREAMS, urllib.quote_plus(game), PAGE_LIMIT)

    streams = JSON.ObjectFromURL(url, cacheTime=CACHE_INTERVAL)

    for stream in streams['streams']:
        subtitle = " %s Viewers" % stream['viewers']
        streamURL = "%s&channel=%s" % (TWITCH_LIVE_PLAYER, stream['channel']['name'])
        dir.Append(WebVideoItem(streamURL, title=stream['channel']['display_name'], summary=stream['channel']['status'], subtitle=subtitle, thumb=stream['channel']['banner'], duration=0))

    return dir


def SearchResults(sender, query=None):
    dir = MediaContainer()

    results = JSON.ObjectFromURL("%s?query=%s&limit=%s" % (TWITCH_SEARCH_STREAMS, urllib.quote_plus(query), PAGE_LIMIT), cacheTime=CACHE_INTERVAL)

    for stream in results['streams']:
        subtitle = "%s\n%s Viewers" % (stream['game'], stream['viewers'])
        streamURL = "%s&channel=%s" % (TWITCH_LIVE_PLAYER, stream['channel']['name'])
        dir.Append(WebVideoItem(streamURL, title=stream['channel']['display_name'], summary=stream['channel']['status'], subtitle=subtitle, thumb=stream['channel']['banner']))
    if len(dir) > 0:
        return dir
    else:
        return MessageContainer("Not found", "No streams were found that match your query.")
