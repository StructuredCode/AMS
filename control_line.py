#!/usr/bin/python3
# -*- coding: utf-8 -*-
import ams
import rospy
from geometry_msgs.msg import Twist
from amsagv_msgs.msg import LineStamped, TagStamped
from math import pi, sin, cos, isnan
from world import MTAG
from amsagv_msgs.msg import ActionsStamped

action_msg_num = 0

class ActionSequence:

    def __init__(self, action_msg): 
        global action_msg_num
        action_msg_num += 1

        self._curr_act_num = 0  #current action number
        self.actions = action_msg
        self.msg_num = action_msg_num

    @property
    def action(self):
        return self.action_msg[self.curr_act_num]

    def next_dir(self):
        return self.actions.name

    def next_tag(self):
        return self.action.id

    def next_dist(self):
        return self.action.distance

    # @curr_act_num.setter
    # def curr_act_num(self, num):
    #     self.action = num


tag = None
p = 2.5
err = 0
# 0- left, 1 - strait, 2- right
direction = 1
#i = 0
s_distance = 0

actions = None


def handleActions(msg):
    global i
    i = 0
    global actions
    actions = msg.actions
    

    # actions = ActionSequence(msg)

        
        # print(len(msg.actions)) 
        # print(msg.actions[0].action.name + ' ' +)

        # print('Next tag: {} -> {}'.format(msg.tag.id, tag))
   

# Handle line senso


def handleLine(msg):

        if actions != None:
            length = len(actions)
            global i
            global s_distance
            global tag 
            if i < length:

                action = actions[i].action

                    # next data
                n_direction = action.name
                n_tag = action.id
                n_dist = action.distance

                    #current data
                lineLeft = msg.line.left if not isnan(msg.line.left) else None
                lineRight = msg.line.right if not isnan(msg.line.right) else None
                distance = msg.line.distance if not isnan(msg.line.distance) else None
                #print('Distance: {} -> {}'.format(msg.line.distance, distance))

                c_distance = distance - s_distance

                if lineLeft == None or lineRight == None: #to je zdaj 2x vecja moznost napake
                    v = 0
                    w = 0
                else:
                    if n_tag > 99:  # samo prevozi distanco kot misli
                        if c_distance < n_dist:
                            if n_direction == "left":
                                err = lineLeft - 0.35
                                print('Action left: {}'.format(msg.line.left, lineLeft))
                            elif n_direction == "right":
                                err = lineRight + 0.55
                                print('Action Rigt: {}'.format(msg.line.right, lineRight))
                            else:
                                err = lineLeft + lineRight

                            v = 0.08
                            w = err * p
                            msgCmdVel = Twist()
                            msgCmdVel.linear.x = v
                            msgCmdVel.angular.z = w
                            # Publish velocity commands
                            pubCmdVel.publish(msgCmdVel)

                        else:
                            i = i + 1
                            s_distance = n_dist + s_distance

                    if n_tag < 99:  #je fizicni tag, caka na scan
                        if c_distance < 1.1 * n_dist:
                            if n_direction == "left":
                                err = lineLeft - 0.35
                            elif n_direction == "right":
                                err = lineRight + 0.55
                            else:
                                err = lineLeft + lineRight

                            v = 0.08
                            w = err * p
                            msgCmdVel = Twist()
                            msgCmdVel.linear.x = v
                            msgCmdVel.angular.z = w
                            # Publish velocity commands
                            pubCmdVel.publish(msgCmdVel)

                            if n_tag == tag:
                                i = i + 1
                                s_distance = n_dist + s_distance
                        else:
                            i = i + 1
                            s_distance = n_dist + s_distance

            else:
                
                v = 0.0
                w = 0.0
                msgCmdVel = Twist()
                msgCmdVel.linear.x = v
                msgCmdVel.angular.z = w
                # Publish velocity commands
                pubCmdVel.publish(msgCmdVel)
        else:
            pass


def handleTag(msg):
  global tag
  tag = MTAG.get(msg.tag.id, None)
  print('New tag: {} -> {}'.format(msg.tag.id, tag))



try:
  rospy.init_node('control_line')
  
  # Velocity commands publisher.
  pubCmdVel = rospy.Publisher('cmd_vel', Twist, queue_size=1)
  # Line sensor subscriber
  subLine = rospy.Subscriber('line', LineStamped, handleLine)
  # Tag subscriber
  subTag = rospy.Subscriber('tag', TagStamped, handleTag)
  # Action subscriber
  sub_actions = rospy.Subscriber('path_actions', ActionsStamped, handleActions)

  rospy.spin()
except KeyboardInterrupt:
  pass