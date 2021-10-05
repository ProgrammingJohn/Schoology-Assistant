import schoolopy
import yaml

yaml.warnings({'YAMLLoadWarning': False})

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

def get_period_ids(relavant_classes, period):
    period_ids = []
    for i in relavant_classes:
        period_ids.append(i['period'][period]['period_id'])
    return period_ids

# ================================================================================

def get_user_grades_GPA(sc):
    sections = Section(sc.get_user_sections(user_id=sc.get_me().uid))

    # gets all current enrolled courses

    grades = Grade(sc.get_user_grades(user_id=sc.get_me().uid))

    # returns big dictionary with Grade objects

    relavant_classes = grades.parse_section(sections.get_course_ids())

    # parses through grade objects
    # idenifies the relavent course's ids from the ones found in the get_user_sections.
    # it compares all the course ids to the relavent ones and picks them out

    period_ids = get_period_ids(relavant_classes, -1)

    # each course contains an period id other than a course one
    # the period id is needed to locate final grade in the final grades list so 
    # it grabs -1 index (the most recent) period ids

    tot_grades = grades.get_grades(relavant_classes, period_ids)

    # iterates through classes
    # for each grading period in the clases final grades
    # if the grading period's id in the relavent periods ids
    # then returns grades found in that period

    titles = sections.get_course_titles()
    title_keys = list(titles)
    grade_keys = list(tot_grades)

    print(f'{sc.get_me().name_display}\'s grades:')

    added_grade = 0
    for i in grade_keys:
        added_grade += float(tot_grades[i])
        print(f'{tot_grades[i]} : {titles[i]}')
    print(f'GPA: {round(added_grade/len(grade_keys), 2)}%')


# ================================================================================

if __name__ == "__main__":

    with open('schoolopy_keys.yaml', 'r') as f:
        cfg = yaml.load(f)

    sc = schoolopy.Schoology(schoolopy.Auth(cfg['key'], cfg['secret']))
    sc.limit = 10  # Only retrieve 10 objects max

    get_user_grades_GPA(sc)
    


