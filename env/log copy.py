import schoolopy
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

def get_period_id(relavant_class, period):
    period_ids = {}
    for a in relavant_class.data:
        grade = Grade(a)
        period_ids[grade.data['section_id']] = grade.data['period'][period]['period_id']
    return period_ids

# ================================================================================

def get_display_user_grades(sc):
    uid = sc.get_me().uid
   
    sections = Section(sc.get_user_sections(user_id=uid))
    course_titles = sections.course_titles
    added_grade = 0
    x = 0
    alert_text = ""
    alert_text += ('\n' + '='*30) + '\n'
    alert_text += f'{sc.get_me().name_display}\'s grades: \n'
    alert_text += ('='*30) + '\n'
    classes = []
    for i in sections.ids:
        section_grade = Grade(sc.get_user_grades_by_section(uid, i))
        if section_grade.data != []:
            x += 1
            period_dict = get_period_id(section_grade, -1)
            period = section_grade.data[-1]['final_grade']
            final_grade = period[-1]['grade']
            alert_text += f"{course_titles[i]} : {final_grade} \n"
            classes.append((i, str(final_grade)))
            added_grade += final_grade
    alert_text += f"GA: {round(added_grade/x, 2)}%\n"
    grade_average = str(round(added_grade/x, 2))
    print(alert_text)
    return grade_average, classes

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
    key = ''
    secret = ''

    sc = schoolopy.Schoology(schoolopy.Auth(key, secret))
    uid = sc.get_me().uid

    GA, classes = get_display_user_grades(sc)

    sections = Section(sc.get_user_sections(user_id=uid))

    course_titles = sections.course_titles

    if not exists(os.getcwd() + '/schoology_grades.csv'):
        create_data_file(course_titles, classes)

    now = dt.datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    
    csv_string = [f"{date}"]
    
    with open('schoology_grades.csv', 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        for i in classes:
            csv_string.append(f"{i[1]}")
        csv_string.append(GA)
        csvwriter.writerow(csv_string)

    plot_grades()

            
# ================================================================================

if __name__ == "__main__":
    main()





