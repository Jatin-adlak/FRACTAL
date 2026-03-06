from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from .camera_stream import gen_frames, start_camera, stop_camera

def dashboard(request):
    return render(request, "dashboard.html")

def start_system(request):
    start_camera()
    return JsonResponse({"status": "started"})

def stop_system(request):
    stop_camera()
    return JsonResponse({"status": "stopped"})

def video_feed(request):
    return StreamingHttpResponse(
        gen_frames(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )
