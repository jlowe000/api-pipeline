import sys

from django.http import HttpResponseRedirect
from django.shortcuts import render

# internal project
sys.path.append('src/scripts')
from pipeline import adb

def upload_file(request):
  if request.method == 'POST':
    print('hello upload_file')
    print(request)
    print(request.FILES)
    t = request.POST.get('tablename')
    f = request.FILES.get('filename',None)
    if f != None:
      print(f.name)
      # with open('/tmp/'+f.name, 'wb+') as destination:
      #   for chunk in f.chunks():
      #    destination.write(chunk)
      adb.store_sample(t,adb.readupload_sample(f))
      adb.expose_sample(t)
  return render(request, 'upload.html', {})

def delete_file(request):
  if request.method == 'POST':
    print('hello delete_file')
    print(request)
    t = request.POST.get('tablename')
    adb.drop_sample(t)
  return render(request, 'delete.html', {})
