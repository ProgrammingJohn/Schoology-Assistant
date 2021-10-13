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

def get_period_id(relavant_class, period):
    period_ids = {}
    for a in relavant_class.data:
        grade = Grade(a)
        period_ids[grade.data['section_id']] = grade.data['period'][period]['period_id']
    return period_ids

# ================================================================================

def get_user_grades(sc):
    uid = sc.get_me().uid
   
    sections = Section(sc.get_user_sections(user_id=uid))
    course_titles = sections.course_titles
    added_grade = 0
    x = 0
    print('\n' + '='*30)
    print(f'{sc.get_me().name_display}\'s grades:')
    print('='*30)
    for i in sections.ids:
        section_grade = Grade(sc.get_user_grades_by_section(uid, i))
        if section_grade.data != []:
            x += 1
            period_dict = get_period_id(section_grade, -1)
            period = section_grade.data[-1]['final_grade']
            final_grade = period[-1]['grade']
            print(f"{course_titles[i]} : {final_grade}")
            added_grade += final_grade
    print(f"GA: {round(added_grade/x, 2)}%\n")


# ================================================================================

if __name__ == "__main__":

    with open('/Users/25ExterkampJ/Desktop/schoology_assistant/schoolopy_keys.yaml', 'r') as f:
        cfg = yaml.load(f)

    sc = schoolopy.Schoology(schoolopy.Auth(cfg['key'], cfg['secret']))
    sc.limit = 10  # Only retrieve 10 objects max

    get_user_grades(sc)






    
    


