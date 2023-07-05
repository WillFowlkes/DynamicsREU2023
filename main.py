import pandas
import numpy
import matplotlib
import parameter



def main():

    parameters = parameter.Parameter()
    parameters.setAll()
    parameters.set("b")
    print(parameters.get("b"))

    print("printing results...")

if __name__ == '__main__':
    main()
