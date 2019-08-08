'''
Created on Jul 26, 2018

@author: cjm10
'''
import json
import logging
import traceback
import urllib
import urllib2
'''This page can be used AS IS with the exception of the CO_PUBLIC and CO_PRIVATE variables'''

class B2f(): 
    #change this!
    COMPANY_KEY = "1q7a5efXjoKmGCLxtA"
    
    #not these
    SUCCESS = 1
    PENDING = 0
    UNRESPONSIVE = -2
    FAILURE = -1
    COOKIE_NOT_FOUND = -3;
    LOUD_PUSH_SENT = -5;
    BASE_B2F = "https://secure.blue2factor.com"
    endpoint = BASE_B2F + "/b2f-prox"
    
    class B2fResponse():
        outcome = 0
        completionUrl = ""
        
        def __init__(self, outcome, completionUrl):
            self.outcome = outcome
            self.completionUrl = completionUrl
            
        def setOutcome(self, outcome):
            self.outcome = outcome
            
        def getOutcome(self):
            return self.outcome
        
        def setCompletionUrl(self, completionUrl):
            self.completionUrl = completionUrl
            
        def getCompletionUrl(self):
            return self.completionUrl
    
    def getBlue2FactorSuccess(self, request):
        return self.b2fValidated(request) == self.SUCCESS
        
    def b2fValidated(self, request):
        ipAddress = self.getClientIp(request)
        b2fId = self.getCookie(request, "b2fIdb") 
        referrer = self.getReferrer(request)
        outcome = self.FAILURE
        completionUrl = ""
        try:
            if b2fId == None or b2fId == "":
                outcome = self.COOKIE_NOT_FOUND
            else:
                params = {'tok' : b2fId, 'uip': ipAddress, 'coId': self.CO_KEY, 
                      'b2fbe': 'bak28', 'referrer': referrer}
                data = urllib.urlencode(params)
                opener = urllib2.build_opener()
                f = opener.open(self.endpoint, data=data)
                jsonStr = f.read()
                logging.info(jsonStr)
                jsonDict = json.loads(jsonStr)
                if jsonDict is not None:
                    outcome = int(jsonDict["result"]["outcome"])
                    reason = jsonDict["result"]["reason"]
                    if outcome != self.SUCCESS:
                        if reason == "unresponsive":
                            outcome = self.UNRESPONSIVE
                    else:
                        completionUrl = reason
        except urllib2.HTTPError, e:
            logging.error(e.code)
            logging.error(e.msg)
            logging.error(e.headers)
            logging.error(e.fp.read())
        except Exception:
            logging.error(traceback.format_exc())
        return self.B2fResponse(outcome, completionUrl)
    
    def getVariable(self, request, varName):
        retVar = self.getPostVariable(request, varName)
        if retVar == '':
            retVar = self.getGetVariable(request, varName)
        return retVar
    
    def getPostVariable(self, request, varName):
        return request.POST.get(varName, '')
    
    def getGetVariable(self, request, varName):
        return request.GET.get(varName, '')
        
    def getReferrer(self, request):
        return request.META.get('HTTP_REFERER')
    
    def getClientIp(self, request):
        return request.META.get('REMOTE_ADDR')
        
    def getCookie(self, request, keyName):
        return request.COOKIES.get(keyName) 
    
    def getModelValues(self, request):
        deviceId = self.getVariable(request, "deviceId")
        deviceVal = self.getVariable(request, "deviceVal")
        b2fId = self.getVariable(request, "b2fid")
        mobile = self.getVariable(request, "mob") == "1"
        mobileInstall = False
        fromJs = self.getVariable(request, "fromJs") == "true"
        fromQr = self.getVariable(request, "fromQr") == "true"
        response = None
        if deviceId == "":
            if b2fId == "" and mobile:
                mobileInstall = True
            else:
                showOutcome = True
                if b2fId == "":
                    self.getCookie(request, "b2fIdb")
                response = self.b2fValidated(request)
        model = self.buildModel(response, deviceId, deviceVal, b2fId, mobileInstall, fromJs, fromQr, showOutcome)
        return model
    
    def buildModel(self, response, deviceId, deviceVal, b2fId, mobileInstall, fromJs, fromQr, showOutcome):
        
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
                "coId": B2f().CO_KEY,
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
