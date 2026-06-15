from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": True,
        "message": "The server is running."
    })