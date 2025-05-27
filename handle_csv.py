import os



FILE_PATH = f"""{os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 'data', 'books.csv'))}"""
def convert_csv(data):
    with open(FILE_PATH,'w', newline='') as csvfile:
        csvfile.write(data)
    booklist=load_csv(FILE_PATH)
    return booklist



def save_csv(data):
    pass



def load_csv(FILE_PATH):
    with open(FILE_PATH, 'r') as csfile:
        lines = csfile.readlines()

    return lines



def main():
    load_csv(FILE_PATH)

if __name__ == '__main__':
        main()
