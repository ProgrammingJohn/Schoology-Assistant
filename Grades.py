import schoolopy, pyautogui
import csv, os
import datetime as dt
from os.path import exists
from matplotlib import pyplot as plt
import matplotlib.dates as mdates


# ================================================================================

class Section:
    def __init__(self, data):
        # data = list of Section elements contaning dicts
        self.ids = []
        self.amount = len(data)
        self.course_titles = {}
        for i in range(self.amount):
            self.ids.append(data[i]['id'])
            self.course_titles[data[i]['id']] = data[i]['course_title']

    def get_course_ids(self):
        return self.ids

    def get_course_titles(self):
        return self.course_titles
 
# ================================================================================

class Grade:
    def __init__(self, data):
        self.data = data
        self.relavant_classes = []

    def parse_section(self, ids):
        for grade_item in self.data:
            section_id = grade_item['section_id']
            if section_id in ids:
                for i in ids:
                    if section_id == i:
                        self.relavant_classes.append(grade_item)
        return self.relavant_classes

    def get_grades(self, relavant_classes, period_ids):
        grades = {}
        for class_ in relavant_classes:
            for period in class_['final_grade']:
                if period['period_id'] in period_ids:
                    grades[class_['section_id']] = period['grade']

        return grades

# ================================================================================

# ================================================================================

def get_display_user_grades():
    sc = schoolopy.Schoology(schoolopy.Auth('ece95872cd2fd46b536c91b023e42381060a6a114', 'df72f273723606b26c1360519dbda860'))
    uid = sc._get('users/me')['id']
    sections = sc._get(f'users/{uid}/sections')
    max = 0
    graded_classes = 0
    classes = []
    GAs = []

    alert_text = ""
    alert_text += ('\n' + '='*30) + "\n"
    alert_text += f'{sc.get_me().name_display}\'s grades: \n'
    alert_text += ('='*30) + '\n'

    for item in sections['section']:
        id = item['id']
        section_grade = sc._get(f"users/{uid}/grades?section_id={id}")
        section = section_grade['section']
        if section:
            num_of_periods = len(section[-1]['final_grade']) - 1
            if num_of_periods > max:
                max = num_of_periods

    GAs = [0 for i in range(num_of_periods)]

    for item in sections['section']:
        id = item['id']
        name = item['course_title']
        classes.append([id, name])
        section_grade = sc._get(f"users/{uid}/grades?section_id={id}")
        section = section_grade['section']
        if section:
            graded_classes += 1
            num_of_periods = len(section[-1]['final_grade']) - 1
            quarter_list = section[-1]['final_grade']
            for i in range(0, num_of_periods):
                GAs[i] = GAs[i] + quarter_list[i+1]['grade']
                classes[-1].append(quarter_list[i]['grade'])
            classes[-1].append(quarter_list[-1]['grade'])
            alert_text += f"{name} : {quarter_list[-1]['grade']}\n"
            final_grade = quarter_list[-1]['grade']
    GA = 0
    print(GAs)
    for i, item in enumerate(GAs):
        GAs[i] = item / graded_classes
        GA = GA + item / graded_classes
    alert_text += "GA: "+ str(round(GA/2,2)) + '\n'

    master = []
    master.append(classes)
    master.append(GAs)
    master.append(GA)
    pyautogui.alert(alert_text)
    return master

def create_data_file(course_titles, classes):
    with open(os.getcwd() + '/schoology_grades.csv', 'w+') as csvfile:
            header = []
            csvwriter = csv.writer(csvfile)
            header.append('')
            for i in classes:
                header.append(course_titles[i[0]])
            header.append('')
            csvwriter.writerow(header)
            header = ['time']
            for i in classes: 
                header.append(i[0])
            header.append('GA')
            csvwriter.writerow(header)

def plot_grades():
    plt.style.use('seaborn-paper')

    with open('schoology_grades.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        rows = [row for row in csvreader]

    for row in rows:
        if row == []:
            rows.remove(row)
            
    headers = rows[0][1:-1]
    column_key = rows[1:][0][1:-1]
    rows = rows[2:]
    time_stamp_data = []
    class_grades = {}
    grade_averages = []

    for a in column_key:
        class_grades[a] = []


    for row in rows:

        time_stamp_data.append(row[0].replace(' ', '\n'))
        grade_averages.append(float(row[-1]))

        for i, grade in enumerate(row[1:-1]):

            class_grades[column_key[i]].append(float(grade))

    x = [dt.datetime.strptime(d,"%d/%m/%Y %H:%M:%S") for d in time_stamp_data]
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y %H:%M"))
    # plt.gca().xaxis.set_major_locator(mdates.HourLocator())

    for i, class_ in enumerate(class_grades):

        plt.plot_date(x, class_grades[class_], linestyle="solid",label=headers[i])

    plt.plot_date(x, grade_averages, linestyle="--", color="#444444", label="GA")
    plt.gcf().autofmt_xdate()
    # date_format = mdates.DateFormatter('%b/%d/%Y %H')
    # plt.gca().xaxis.set_major_formatter(date_format)
    plt.xlabel("Date")
    plt.tick_params(labelsize=7)
    plt.ylabel("Grade")
    plt.title("Grades")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():

    sc = schoolopy.Schoology(schoolopy.Auth('', ''))
    uid = sc.get_me().uid

    master = get_display_user_grades()

    if not exists(os.getcwd() + '/schoology_grades.csv'):
        create_data_file(course_titles, classes)

    now = dt.datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    
    csv_string = [f"{date}"]

    graded_classes=[x for x in master[0] if len(x)>2]

    # print(graded_classes)
    with open('schoology_grades.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        ids_order = [row for row in csvreader][1:2][0][1:-1]
    
    with open('schoology_grades.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        for i in ids_order:
            print('id: '+i)
            for item in graded_classes:
                if i in item:
                    print(item)
                    csv_string.append(f"{item[-1]}")

        csv_string.append(master[-1]/len(master[-2]))
        csvwriter.writerow(csv_string)


    plot_grades()

            
# ================================================================================

if __name__ == "__main__":
    main()





