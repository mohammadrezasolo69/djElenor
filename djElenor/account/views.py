from django.http import HttpResponse
from ..melipayamak import Api


def sms_view(request):
    username = '******'
    password = '******'
    api = Api(username, password)
    sms_soap = api.sms('soap')
    to = '091*******'
    text = [123456]
    bodyId = 208961
    sms_response = sms_soap.send_by_base_number(text, to, bodyId)
    print(sms_response)

    return HttpResponse("Hello world!")
