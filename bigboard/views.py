from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import paramiko
import re
from .models import *

def home(request):
    robots = Robot.objects.all()
    return render(request, 'home.html', {'robots': robots})

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
            try:
                rb = Robot.objects.get(ip=robot['ip'])
                rb.name = robot['robot']
                rb.time = robot['time']
                rb.save()
            except Robot.DoesNotExist:
                rb = Robot(ip=robot['ip'], name=robot['robot'], time=robot['time'])
                if len(robot['robot']) > 5:
                    rb.type = RobotTypeA.objects.create()
                else:
                    rb.type = RobotTypeB.objects.create()
                rb.save()
            robot = {}

@method_decorator(csrf_exempt)
def perform_action(request, action, pk):
    input = request.POST.get('input', None)
    result = {}
    try:
        robot = Robot.objects.get(id=pk)
        allActions = robot.type.actions.replace(' ', '').lower()
        if action in allActions:
            perform(robot, action, input, result)
        else:
            result['error'] = "Robot " + robot.name + ' does not have action ' + action
    except Robot.DoesNotExist:
        result['error'] = "Robot with id " + str(pk) + " does not exist"
    return JsonResponse(result)


def perform(robot, action, input, result):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(robot.ip, 22, "mhc", "mhcrobots", timeout=5)
        command = "cd actions; echo " + input + " > " + action + ".txt"
        (stdin, stdout, stderror) = ssh.exec_command(command, timeout=5)
        if len(stderror.readlines()) > 0:
            result['error'] = 'Cannot perform action on robot ' + robot.name
    except Exception:
        result['error'] = 'Cannot connect to / perform action on robot ' + robot.name

