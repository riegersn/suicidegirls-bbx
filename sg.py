#
# SuicideGirls
# Manages user authentication, searching and content with the SuicideGirls API.
#
# by Shawn Rieger / Boxee
#

import mc
import re
import sys
import urllib
import time


def quickLaunch(id):
    mc.GetApp().ActivateWindow(id, mc.Parameters())


def launch(id, params):
    p = mc.Parameters()
    for i in params:
        p[i] = params[i]
    mc.GetApp().ActivateWindow(id, p)


def hasAuth():
    reg = mc.GetApp().GetLocalConfig()
    if reg.GetValue("authenticated"):
        return True
    return False


def playFrontSet(id):
    config = mc.GetApp().GetLocalConfig()
    if config.GetValue("authenticated"):
        list = mc.GetActiveWindow().GetList(120)
        item = list.GetItem(id)
        params = {
            "url":			item.GetPath(),
            "model":		item.GetProperty("model"),
            "set":			item.GetProperty("set"),
            "thumb":		item.GetImage(2),
            "photographer":	item.GetProperty("photographer-name"),
            "date":			"Join Today!"
        }
        launch(14003, params)
    else:
        mc.ShowDialogNotification(
            'Please sign in to view this set and others.', "sg_icon_notification.png")


def check_authentication():
    sg = mc.Http()
    config = mc.GetApp().GetLocalConfig()
    mc.ShowDialogWait()
    mc.LogDebug('SuicideGirls: Checking active authentication.')
    sg.SetUserAgent(
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/2007091417 Firefox/2.0.0.7')
    http = sg.Get('http://suicidegirls.com/api/loggedin.php')
    mc.HideDialogWait()

    mc.LogDebug('SuicideGirls: Session check responded with: ' + http)

    if 'name:' in http:
        config.SetValue('authenticated', 'true')
        mc.LogDebug('SuicideGirls: User is still authenticated.')
        return True

    mc.LogDebug('SuicideGirls: User is no longer authenticated.')
    config.Reset('authenticated')
    config.Reset('username')
    config.Reset('password')
    return False


def login_sg(user, password):
    sg = mc.Http()
    mc.LogDebug('SuicideGirls: Authentication start')
    mc.ShowDialogNotification(
        "Authenticating to SuicideGirls...", "sg_icon_notification.png")
    mc.ShowDialogWait()
    config = mc.GetApp().GetLocalConfig()
    params = 'password=' + password + '&username=' + user + '&action=process_login'
    mc.LogDebug('SuicideGirls: params: ' + params)
    sg.SetUserAgent(
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/2007091417 Firefox/2.0.0.7')
    sg.Get('http://suicidegirls.com/')
    sg.SetHttpHeader('Content-Type', 'application/x-www-form-urlencoded')
    sg.Post('http://suicidegirls.com/login/', params)
    responseCookie = str(sg.GetHttpHeader("Set-cookie"))
    mc.LogDebug('SuicideGirls: response: ' + responseCookie)
    mc.HideDialogWait()

    if 'PHPSESSID=' in responseCookie:
        config.SetValue('authenticated', 'true')
        config.SetValue('username', user)
        config.SetValue('password', password)
        mc.ShowDialogNotification(
            "Welcome to SuicideGirls!", "sg_icon_notification.png")
        mc.LogDebug('SuicideGirls: Authentication successfull')
        return True
    else:
        mc.ShowDialogNotification(
            "Authentication failed!", "sg_icon_notification.png")
        mc.LogDebug('SuicideGirls: Authentication failed: no reason given')

    config.Reset('authenticated')
    config.Reset('username')
    config.Reset('password')
    return False


def logout_sg():
    sg = mc.Http()
    mc.LogDebug('SuicideGirls: User logged out manually.')
    win = mc.GetActiveWindow()
    win.GetLabel(201).SetLabel("")
    win.GetButton(202).SetLabel("LOGIN")
    config = mc.GetApp().GetLocalConfig()
    config.Reset('authenticated')
    config.Reset('username')
    config.Reset('password')
    quickLaunch(14000)


def clear_login():
    mc.GetActiveWindow().GetEdit(701).SetText("")
    mc.GetActiveWindow().GetEdit(702).SetText("")


def search_sg(string):
    # returns a list of search results
    try:
        if not string:
            items = mc.ListItems()
            mc.GetActiveWindow().GetList(130).SetItems(items)
            return False

        mc.ShowDialogWait()
        url = ""
        sg = mc.Http()
        string = string.capitalize()
        searchUrl = "http://suicidegirls.com/media/generated/girlindex%s/last_set/1.xml"
        for i in range(1, len(string) + 1):
            url += "/" + string[0:i]

        html = sg.Get(searchUrl % (url))
        results = re.compile("<alias>(.*?)</alias>").findall(html)

        items = mc.ListItems()
        for girl in results:
            item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            item.SetLabel(girl)
            item.SetPath(
                "rss://dir.boxee.tv/apps/suicidegirls/girls/model=%s" % (urllib.quote(girl)))
            item.SetThumbnail(
                "http://img.suicidegirls.com/media/girls/%s/girl_pic_medium.jpg" % (urllib.quote(girl)))
            #~ item.SetProperty("Image0", "http://img.suicidegirls.com/media/girls/%s/girl_pic_large.jpg")
            #~ item.SetProperty("Image0", "http://img.suicidegirls.com/media/girls/%s/girl_pic_medium.jpg")
            items.append(item)

        print len(items)
        mc.GetActiveWindow().GetList(130).SetItems(items)
        mc.HideDialogWait()
    except:
        mc.HideDialogWait()
        mc.GetActiveWindow().GetList(130).SetItems(mc.ListItems())
        mc.ShowDialogNotification(
            "An error has occurred while searching!", "sg_icon_notification.png")
        mc.LogError("SuicideGirls: %s - %s" % (sys.exc_info()[:2]))
        return False
