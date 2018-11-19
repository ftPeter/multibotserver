from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import paramiko
import pytz
import re
from .models import *

### HOMEPAGE
def home(request):
    active = Robot.objects.filter(active=True)
    inactive = Robot.objects.filter(active=False)
    return render(request, 'home.html', {'activeRobots': active, 'inactiveRobots': inactive})


#### REFRESH DATABASE
@method_decorator(csrf_exempt)
def refresh_robot_data(request):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = {}
    try:
        ssh.connect("multirobotics.peterklemperer.com", 22, "multirobotics", "ZwUhQmcym8", timeout=5)

        command = "cd multirobotics.peterklemperer.com; cd multi-robotics-status; cd _data; cat *.yml"
        (stdin, stdout, stderror) = ssh.exec_command(command, timeout=5)
        if len(stderror.readlines()) > 0:
            result['error'] = 'Error fetching data from server.'
        else:
            output = stdout.readlines()
            update_database(output)
    except Exception:
        result['error'] = 'Failed to connect/fetch data from server.'
    return JsonResponse(result)


def update_database(output):
    robot = {}
    for i in output:
        line = re.split(': |\n', i)
        robot[line[0]] = line[1]
        if line[0] == 'ip':
            active = get_active_status(robot['time'])
            try:
                rb = Robot.objects.get(name=robot['robot'])
                rb.ip = robot['ip']
                rb.time = robot['time']
                rb.active = active
                rb.save()
            except Robot.DoesNotExist:
                rb = Robot(ip=robot['ip'], name=robot['robot'], time=robot['time'], active=active)
                rb.type = RobotTypeA.objects.create()
                rb.save()
            robot = {}

def get_active_status(time):
    try:
        datetime_obj = datetime.strptime(time, '%Y-%m-%d_%H-%M-%S').replace(tzinfo=None)
        now = datetime.now(pytz.timezone('US/Eastern')).replace(tzinfo=None)
        difference = (now - datetime_obj).total_seconds() / 60.0
        if difference <= 15:
            return True
        else:
            return False
    except Exception:
        return False



### PERFORM ACTION ON A ROBOT
@method_decorator(csrf_exempt)
def perform_action(request, pk, action):
    input = request.POST.get('input', None)
    result = {}
    try:
        robot = Robot.objects.get(id=pk)
        allActions = robot.type.actions.replace(' ', '').lower()
        if action in allActions:
            perform(robot, action, input, result)
        else:
            result['error'] = "Robot " + robot.name + " does not have action " + action
    except Robot.DoesNotExist:
        result['error'] = "Robot with id " + str(pk) + " does not exist"
    return JsonResponse(result)


def perform(robot, action, input, result):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(robot.ip, 22, "mhc", "mhcrobots", timeout=5)

        command = ["cd multi-robotics/MRS-Controller/romi_utilities/"]
        if action == "changecolor":
            command.append("python3 pixel_utility.py " + input)

        elif action == "checkbattery":
            command.append("python3 battery_utility.py")

        elif action == "takepicture":
            command.append("cd /home/mhc/multi-robotics/gallery/")
            filename = str(datetime.now().strftime("%Y%m%d%H%M%S")) + ".jpg"
            command.append("raspistill -o " + filename)
            c = 'curl -s -S -i -X POST -H "Content-Type: multipart/form-data" -F "data=@' + filename + '" '
            c += 'http://multibot.cs.mtholyoke.edu/' + str(robot.id) + '/uploadimage'
            command.append(c)

        (stdin, stdout, stderror) = ssh.exec_command('; '.join(command), timeout=10)
        if len(stderror.readlines()) > 0:
            result['error'] = 'Cannot perform action ' + action + ' on robot ' + robot.name
        else:
            result['result'] = ''.join(stdout.readlines())

    except Exception:
        result['error'] = 'Cannot connect to robot ' + robot.name



### GALLERY IMAGE OF ROBOTS
def show_gallery(request):
    robots = [robot.robot for robot in RobotTypeA.objects.all()]
    return render(request, 'gallery.html', {'robots': robots})

def show_indiv_gallery(request, pk):
    try:
        robot = Robot.objects.get(id=pk)
        allActions = robot.type.actions.replace(' ', '').lower()
        if 'takepicture' in allActions:
            return render(request, 'indiv_gallery.html', {'robot': robot})
        else:
            return render(request, 'error.html', {'error': 'Robot ' + robot.name + ' does not have a gallery'})
    except Robot.DoesNotExist:
        return render(request, 'error.html', {'error': 'Robot with id ' + str(pk) + ' does not exist'})




### A ROBOT UPLOAD AN IMAGE TO ITS GALLERY
@method_decorator(csrf_exempt)
def upload_image(request, pk):
    result = {}
    if request.method == 'POST':
        data = request.FILES.get('data')
        try:
            robot = Robot.objects.get(id=pk)
            allActions = robot.type.actions.replace(' ', '').lower()
            if 'takepicture' in allActions:
                Image.objects.create(image=data, robot=robot.type)
            else:
                result['error'] = "Robot with id " + str(pk) + " cannot TakePicture"
        except Robot.DoesNotExist:
            result['error'] = "Robot with id " + str(pk) + " does not exist"
    return JsonResponse(result)


