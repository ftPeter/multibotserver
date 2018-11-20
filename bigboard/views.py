from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import paramiko
import pytz
import re
from .utils.web_broadcast import WebBroadcast
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
    input = request.POST.get('input', '')
    result = {}
    try:
        robot = Robot.objects.get(id=pk)
        if robotCan(action, robot):
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

        if action == "takepicture":
            command.append("cd /home/mhc/multi-robotics/gallery/")
            filename = str(datetime.now().strftime("%Y%m%d%H%M%S")) + ".jpg"
            command.append("raspistill -o " + filename)
            c = 'curl -s -S -i -X POST -H "Content-Type: multipart/form-data" -F "data=@' + filename + '" '
            c += 'http://multibot.cs.mtholyoke.edu/' + str(robot.id) + '/uploadimage'
            command.append(c)
        else:
            command.append(getCommand(action, input))

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
        if robotCan('takePicture', robot):
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
            if robotCan('takePicture', robot):
                Image.objects.create(image=data, robot=robot.type)
            else:
                result['error'] = "Robot with id " + str(pk) + " cannot TakePicture"
        except Robot.DoesNotExist:
            result['error'] = "Robot with id " + str(pk) + " does not exist"
    return JsonResponse(result)




# OPTIONS FOR BROADCAST
def show_broadcast(request):
    active = Robot.objects.filter(active=True)
    # if later, create another type of robot which all actions can be broadcasted, update robotType
    actions = RobotTypeA.objects.all()[:1].get().actions.split(', ')
    if 'Take Picture' in actions:
        actions.remove('Take Picture')
    return render(request, 'broadcast.html', {'robots': active, 'actions': actions})


@method_decorator(csrf_exempt)
def broadcast(request):
    result = {}
    if request.method == 'POST':
        robots = request.POST.get('robots', '')
        input = request.POST.get('input', '')
        action = request.POST.get('action', '')

        if len(robots) == 0:
            return JsonResponse(result)
        else:
            robots = robots.split(',')

        robot_address_list = []
        command = ["cd multi-robotics/MRS-Controller/romi_utilities/", "python3 robot_broadcast.py"]
        input = getCommand(action, input)

        for robot_id in robots:
            try:
                rb = Robot.objects.get(id=int(robot_id))
                result[rb.name] = {}
                if robotCan(action, rb):
                    robot_address_list.append(rb.ip)
                else:
                    result[rb.name]['error'] = 'Robot with id ' + robot_id + ' cannot perform (' + action + ')'
                    result[rb.name]['result'] = ''
            except Robot.DoesNotExist:
                result[rb.name]['error'] = 'Robot with id ' + robot_id + ' does not exist'
                result[rb.name]['result'] = ''

        beb = WebBroadcast(robot_address_list, input, command)
        for output in beb.run():
            name = Robot.objects.get(ip=output[0]).name
            result[name]['result'] = output[1]
            result[name]['error'] = output[2]

    return JsonResponse(result)




# FORMATION EXPERIMENT, KEEP IT STATIC FOR NOW
def show_formation(request):
    return render(request, 'formation.html', {})

def formation(request):
    return


# helper functions
# command to run an action
def getCommand(action, input):
    if action == "changecolor":
        return "./pixel_utility.py " + input
    elif action == "checkbattery":
        return "./battery_utility.py"
    return ''

# whether the robot can perform an action. cross-check the action with the static action list in robot's type
def robotCan(action, robot):
    allActions = robot.type.actions.replace(' ', '').lower()
    if action.lower() in allActions:
        return True
    return False