# -*- coding: utf-8 -*-

from django.http import HttpResponse
from models import Record
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
@csrf_exempt
def addRecord(request):
    try:
        UserID = request.GET["UserID"]
        Time = request.GET["Time"]
        newRecord = Record(UserID=UserID, Time=Time)
        newRecord.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Failer")

def loadRecords(request):
    records = Record.objects.order_by('Time')
    result = ""
    for record in records:
        result = result + record.UserID+","
        result = result + str(record.Time) + ";"
    return HttpResponse(result)