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
    #change these!!
    CO_PUBLIC = "CHANGE_THIS"
    CO_PRIVATE = "AND_THIS" 
    
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
        referrer = self.getReferrer()
        outcome = self.FAILURE
        completionUrl = ""
        try:
            if b2fId == None or b2fId == "":
                outcome = self.COOKIE_NOT_FOUND
            else:
                params = {'tok' : b2fId, 'uip': ipAddress, 'b2fKey': self.CO_PRIVATE, 'coId': self.CO_PUBLIC, 
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
        return request.referer
    
    def getClientIp(self, request):
        return request.META.get('REMOTE_ADDR')
        
    def getCookie(self, request, keyName):
        return request.COOKIES.get(keyName) 
