'''
Created on Sep 15, 2018

@author: cjm10
'''
from Blue2FactorPython.Utilities.Blue2FactorUtil import B2f
from django.shortcuts import render

def Blue2Factor(request):
    model = getModelValues(request)
    return render(request, "Blue2FactorPython/template/blue2factor.html", model)

def getModelValues(request):
    b2f = B2f()
    deviceId = b2f.getVariable(request, "deviceId")
    deviceVal = b2f.getVariable(request, "deviceVal")
    b2fId = b2f.getVariable(request, "b2fid")
    mobile = b2f.getVariable(request, "mob") == "1"
    mobileInstall = False
    fromJs = b2f.getVariable(request, "fromJs") == "true"
    fromQr = b2f.getVariable(request, "fromQr") == "true"
    response = None
    if deviceId == "":
        if b2fId == "" and mobile:
            mobileInstall = True
        else:
            showOutcome = True
            if b2fId == "":
                b2f.getCookie(request, "b2fIdb")
            response = b2f.b2fValidated(request)
    model = buildModel(response, deviceId, deviceVal, b2fId, mobileInstall, fromJs, fromQr, showOutcome)
    return model

def buildModel(response, deviceId, deviceVal, b2fId, mobileInstall, fromJs, fromQr, showOutcome):
    
    if (response != None):
        outcome = response.getOutcome()
        baseUrl = response.getCompletionUrl()
        if outcome == 1:
            outcomeStr = "Success!"
        elif outcome == -1:
            outcomeStr = "Access Denied"
        elif outcome == -2:
            outcomeStr = ("Blue2Factor has blocked access to this page because you do not " + 
                        "have another registered device that could be found nearby.<br/><br/>To learn more click " + 
                        "<a href='//www.blue2factor.com/help'>here</a>.")
        elif outcome == -3:
            outcomeStr = ("Blue2Factor needs to be resynched on this browser.<br/><br/>To learn more click " + 
                        "<a href='//www.blue2factor.com/help'>here</a>.")
        elif outcome == -5:
            outcomeStr = ("A push notification was sent to your phone.  Please respond to access this site.<br/><br/>To learn more click " + 
                        "<a href='//www.blue2factor.com/help'>here</a>.")
        elif outcome == -6:
            outcomeStr = ("You must open Blue2Factor on your phone to gain access to this site.<br/><br/>To learn more click " + 
                        "<a href='//www.blue2factor.com/help'>here</a>.")
    else:
        outcome = 0
        baseUrl = ""
        outcomeStr = ""
    model = {
            "coId": B2f().CO_PUBLIC,
            "fromQr": fromQr,
            "fromJs": fromJs,
            "mobileInstall": mobileInstall,
            "deviceId": deviceId,
            "deviceVal": deviceVal,
            "token": b2fId,
            "showOutcome": showOutcome,
            "outcome": outcome,
            "baseUrl": baseUrl,
            "outcomeString": outcomeStr
        }
    return model


