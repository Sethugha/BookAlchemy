import csv


def main():
    data=[1,1,0,1]

    sort1 = ''
    if data[0] == 1:
        sort1 = 'title,'
    sort2 = ''
    if data[1] == 1:
        sort2 = 'author,'
    sort3 = ''
    if data[2] == 1:
        sort3 = 'publication_year'
    direction = 'asc'
    if data[3] == 1:
        direction = 'desc'
    sort_order = sort1+sort2+sort3
    if sort_order[-1] ==',':
        sort_order = sort_order[:-1]
    print(sort_order, direction)





if __name__ == '__main__':
    main()
