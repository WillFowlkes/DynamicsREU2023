class Parameter:

    def __init__(self):
        self.__dictionary = {"N": 1,
                             "n": 1,
                             "r": 1,
                             "c": 1,
                             "Rmin": 1,
                             "Rmax": 1,
                             "Tmax": 1,
                             "b": 1,
                             "k": 1,
                             "f": 1}

    def setAll(self):
        self.__dictionary["N"] = getNaturalNumber("N")
        n = self.__dictionary["n"] = getNaturalNumber("n")
        r = self.__dictionary["r"] = getPosRealNumber("r")
        Rmin = self.__dictionary["Rmin"] = getNaturalNumber("Rmin")
        Tmax = self.__dictionary["Tmax"] = getNaturalNumber("Tmax")
        self.__dictionary["Rmax"] = Rmin + Tmax * r / n
        self.__dictionary["c"] = self.set_c()
        self.__dictionary["b"] = getPosRealNumber("b")
        self.__dictionary["k"] = getPosRealNumber("k")
        self.__dictionary["f"] = getPosRealNumber("f")

    def set_c(self):
        c = getPosRealNumber("c")
        while self.__dictionary["r"] < c or self.__dictionary["r"] / self.__dictionary["n"] >= c:
            print("c must satisfy the condition r/n < c <= r")
            c = getPosRealNumber("c")
        return c

    def get(self, name):
        return self.__dictionary[name]

    def set(self, name):
        if name == "c":
            self.__dictionary[name] = self.set_c(self)
        elif type(self.__dictionary[name]) == int:
            self.__dictionary[name] = getNaturalNumber(name)
        elif type(self.__dictionary[name]) == float:
            self.__dictionary[name] = getPosRealNumber(name)


def getNaturalNumber(name):
    while True:
        print("Input value of " + name + " (integer values only)")
        N = input()
        try:
            N = int(N)
            if N > 0:
                return N
            else:
                print(name + " must be a positive integer.")
        except ValueError:
            print(name + " must be a positive integer.")


def getPosRealNumber(name):
    while True:
        print("Input value of " + name + " (positive values only)")
        N = input()
        try:
            N = float(N)
            if N > 0:
                return N
            else:
                print(name + " must be a positive number.")
        except ValueError:
            print(name + " must be a positive number.")
