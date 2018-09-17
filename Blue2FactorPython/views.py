'''
Created on Sep 15, 2018

@author: cjm10
'''
import Blue2FactorPython.Utilities.Blue2FactorUtil as B2fUtil
from django.shortcuts import render
from django.views.generic import TemplateView

class Blue2Factor(TemplateView):
    def get(self, request, **kwargs):
        model = B2fUtil.B2f().getModelValues(request)
        return render(request, "blue2factor.html", model)




