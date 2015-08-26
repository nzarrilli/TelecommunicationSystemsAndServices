__author__ = 'nzarrilli'

# Questo script legge il contenuto di un file .txt
# Guida: http://www.afterhoursprogramming.com/tutorial/Python/Reading-Files/

import os


def read_file(file_path):
    try:
        # Open file
        in_file = open(file_path, "r")

        # Read all lines
        for line in in_file:
            print line

        # Close file
        in_file.close()
    except IOError, ex:
        print ex


if __name__ == "__main__":
    # TODO: Modificare la path del file da leggere
    base_dir = os.getenv("HOME")
    pycharm_dir = "PycharmProjects"
    project_dir = "TelecommunicationSystemsAndServices"
    file_dir = "File"
    filename = "Host.txt"
    # Creazione della path completa
    file_path = os.path.join(base_dir, pycharm_dir, project_dir, file_dir, filename)
    read_file(file_path)
