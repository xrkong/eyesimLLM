#!/usr/bin/env python3

import math
import random as rd

import numpy as np
from eye import *


class S4_Robot():

    def __init__(self):
        
        # --- Define variables
        self.min_distance = 300
        self.default_lin_speed = 100
        self.default_omega = 60

        self.PSD_names = np.array([PSD_FRONT, PSD_LEFT, PSD_RIGHT, PSD_BACK])
        self.PSD_val = np.zeros(self.PSD_names.size)
        self.get_PSD_values()

        self.find_start_corner()


    def find_start_corner(self):
        
        # --- Use PSD sensors to verify wall nearby
        VWSetSpeed(100,0)
        while(self.eval_near_wall() == False):
            self.get_PSD_values()
            OSWait(100)

        if(self.PSD_val[2] <= self.PSD_val[1]):
            turn_angle = np.arctan2(self.PSD_val[2], self.PSD_val[0])
            VWTurn(int(np.rad2deg(turn_angle) + 11), 
                   self.default_omega)
            VWWait()
        else:
            turn_angle = np.arctan2(self.PSD_val[1], self.PSD_val[0])
            VWTurn(-int(np.rad2deg(turn_angle) + 8), 
                   self.default_omega)
            VWWait()
            
        # --- Verify the closest perpendicular wall
        self.get_PSD_values()
        if(self.PSD_val[0] >= self.PSD_val[3]):
            VWTurn(180, 
                   self.default_omega)
            VWWait()

        self.follow_near_wall(self.PSD_val[0],self.default_lin_speed)

        VWTurn(180, self.default_omega)
        VWWait()

   
    def follow_near_wall(self, total_distance, speed):

        # --- Mantain constant PSD distance from the wall
        PSD_factor, PSD_index = self.shortest_PSD_measure()

        desired_distance_sPSD = self.PSD_val[2]
        current_distance_sPSD = self.PSD_val[2]

        error_sPSD = desired_distance_sPSD - current_distance_sPSD
        kP = 1

        # --- Calculate travel error
        start_distance_fPSD = self.PSD_val[0]
        current_distance_fPSD = self.PSD_val[0]

        error_fPSD = start_distance_fPSD - current_distance_fPSD

        while (error_fPSD <= total_distance and 
               current_distance_fPSD >= self.min_distance):
            
            VWSetSpeed(speed,int(kP * error_sPSD))

            self.get_PSD_values()
            current_distance_sPSD = self.PSD_val[2]
            current_distance_fPSD = self.PSD_val[0]

            error_sPSD = desired_distance_sPSD - current_distance_sPSD
            error_fPSD = start_distance_fPSD - current_distance_fPSD

            OSWait(100)

        VWSetSpeed(0,0)


    def robot_trajectory(self):
        factor,index = self.shortest_PSD_measure()
        
        for i in range(4):
            self.follow_near_wall(2000,self.default_lin_speed)
            self.turn(factor * 90)
            self.follow_near_wall(200,self.default_lin_speed)
            self.turn(factor * 90)

            self.follow_near_wall(2000,self.default_lin_speed)
            self.turn(factor * -90)
            self.follow_near_wall(200,self.default_lin_speed)
            self.turn(factor * -90)


    def eval_near_wall(self):
        if (self.PSD_val[0] <= self.min_distance or
            self.PSD_val[1] <= self.min_distance or
            self.PSD_val[3] <= self.min_distance):
            VWSetSpeed(0,0)
            return True
        
        else: 
            return False


    def get_PSD_values(self):
        for i in range(self.PSD_names.size):
            self.PSD_val[i] = PSDGet(i+1)


    def turn(self,angle):
        VWTurn(angle, self.default_omega)
        VWWait()


    def shortest_PSD_measure(self):
        self.get_PSD_values()
        if (self.PSD_val[1] <= self.PSD_val[2]):
            factor = -1
            index = 1
        else:
            factor = 1
            index = 2

        return factor, index


def main():

    robot = S4_Robot()
    robot.robot_trajectory()


if __name__ == "__main__":
    main()