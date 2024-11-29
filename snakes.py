class Snake:
    
    def __init__(self, x, y, speed):
        self.__position_x = x
        self.__position_y = y
        self.__length = 1
        self.__speed = speed
        self.__section_radius = 25

    def get_position_x(self):
        return self.__position_x
    
    def get_position_y(self):
        return self.__position_y
    
    def get_length(self):
        return self.__length
    
    def get_speed(self):
        return self.__speed
    
    def add_length(self, number):
        self.__length += number