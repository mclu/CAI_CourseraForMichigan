#!/usr/bin/env python
# coding: utf-8

# Coursera for Michigan - Data Cleaning Script
# Author: Ming-Chen (Amy) Lu (mingchlu@umich.edu)
#
# The script combines UM student term information and enrollments on Coursera for
# Michigan so that the combined data can be used for the visualizations on Tableau.

# ------------------------------------------------------------------------------
# Start of the script
# ------------------------------------------------------------------------------

# Libraries
import pandas as pd
import numpy as np
import datetime as dt

# Read in the files
coursera_enrollment = pd.read_csv('coursera_enrollment_hashed.csv')
student_term = pd.read_csv('student_term_with_descriptions_hashed.csv')
term = pd.read_csv('term.csv')
course = pd.read_csv('coursera_course.csv')
spec = pd.read_csv('coursera_specialization.csv')
specourse = pd.read_csv('coursera_specializationcourses.csv')
dept = pd.read_csv('plan_to_department_mapping.csv')

# Clean up the student_term file: ----------------------------------------------
# Filter student term file by registration_status and withdraw_code
student_term_new = student_term[(student_term['registration_status'] == 'RGSD') &
                                (student_term['withdraw_code'] == 'NWD')]

# Filter the latest term
idx = (student_term_new.groupby(['username'])['term_id'].
       transform(max) == student_term_new['term_id'])
student_term_new = student_term_new[idx]

# Term file provides the descriptions of term_id, we add the term begin/end date to the student term file
term_info = (term.loc[:,['code', 'begin_date', 'end_date']].
             rename(columns={'code': 'term_id','begin_date': 'term_begin_date',
                             'end_date': 'term_end_date'}))
student_term_new = student_term_new.merge(term_info, on='term_id', how='left')
student_term_new.head()

# Clean up the coursera_enrollment file: ---------------------------------------
# Keep only user_id before @umich
coursera_enrollment['id'] = coursera_enrollment['id'].str.split('@').str[0]
coursera_enrollment.rename(columns={'id': 'username'}, inplace=True)

# Remove 'course~' in course_id column
coursera_enrollment['course_id'] = coursera_enrollment['course_id'].str.split('~').str[1]
# Remove 'specialization~' in specialization_id column
coursera_enrollment['specialization_id'] = coursera_enrollment['specialization_id'].str.split('~').str[1]

# Add two columns
coursera_enrollment['is_alumnus'] = np.where(coursera_enrollment.program_id == '2ul8M6yGEeiHrwrBL_30oA', 1, 0)
coursera_enrollment['is_complete'] = np.where(np.isnan(coursera_enrollment.grade), 0, 1)

# Left join course info
course_info = (course.loc[:, ['content_id', 'name']].
               rename(columns={'content_id': 'course_id', 'name': 'course_name'}))
coursera_enrollment = coursera_enrollment.merge(course_info, on='course_id', how='left')

# Left join specialization info
spec = pd.read_csv('coursera_specialization.csv')
specourse = pd.read_csv('coursera_specializationcourses.csv')
spec = (spec.loc[:, ['content_id', 'name']].
        rename(columns = {'content_id': 'specialization_id', 'name': 'specialization_name'}))
specourse = (specourse.loc[:, ['order', 'course_id', 'specialization_id']].
             rename(columns = {'order': 'course_order'}))
specourse['course_id'] = specourse['course_id'].str.split('~').str[1]
specourse['specialization_id'] = specourse['specialization_id'].str.split('~').str[1]
spec_info = specourse.merge(spec[['specialization_id', 'specialization_name']], on='specialization_id')

coursera_enrollment_new = coursera_enrollment.merge(spec_info, on='course_id', how='left')

x = (coursera_enrollment.
     merge(spec_info[['specialization_id', 'specialization_name']], on='specialization_id', how='left').
     drop_duplicates().specialization_name)

coursera_enrollment_new['specialization_name'] = (
    np.where(pd.isnull(coursera_enrollment_new['specialization_name']),
             x, coursera_enrollment_new['specialization_name']))

coursera_enrollment_new.drop('specialization_id_y', axis=1, inplace=True)
coursera_enrollment_new.rename(columns={'specialization_id_x': 'specialization_id'}, inplace=True)

# Inner join student term and Coursera enrollment files: -----------------------
# Extract key columns
enrol_info = ['username', 'enrolled_date', 'last_activity', 'overall_progress',
              'grade', 'course_id', 'course_name','specialization_id', 'specialization_name',
              'course_order', 'is_alumnus', 'is_complete']

std_info = ['username', 'career_id', 'career_description', 'term_id',
            'term_begin_date', 'term_end_date','program_description',
            'primary_plan', 'plan_description', 'student_year']

std_enrol = student_term_new[std_info].merge(coursera_enrollment_new[enrol_info], on='username')

# Further std_enrol file cleanup
# Format the date
std_enrol['term_begin_date'] = pd.to_datetime(std_enrol['term_begin_date']).dt.date
std_enrol['term_end_date'] = pd.to_datetime(std_enrol['term_end_date']).dt.date
std_enrol['enrolled_date'] = pd.to_datetime(std_enrol['enrolled_date'], utc=True).dt.normalize().dt.date

# Randomly drop one of the career when users have two careers
find_dup = std_enrol.groupby(['username'])['career_id'].nunique()
idx = find_dup[find_dup == 2].index.tolist()

size = 1       # sample size
replace = True  # with replacement
fn = lambda obj: obj.loc[np.random.choice(obj.index, size, replace),:].iloc[:,:2]
np.random.seed(1)
rdn_idx = std_enrol[std_enrol.username.isin(np.array(idx))].groupby(['username'], as_index=False).apply(fn)

std_enrol = std_enrol[~(
    (std_enrol['username'].isin(np.array(rdn_idx['username']))) &
    (std_enrol['career_id'].isin(np.array(rdn_idx['career_id'])))
    )]

# Add department info
std_enrol['department'] = std_enrol['primary_plan'].map(dict(zip(dept.plan, dept.dept)))

# check the NaN in primary_plan
#map_dept = std_enrol['primary_plan'].map(dict(zip(dept.plan, dept.dept)))
#std_enrol.loc[np.where(map_dept.isnull())[0].tolist(),['primary_plan', 'plan_description']].drop_duplicates()

# ------------------------------------------------------------------------------
# Export the file and it's good to import into Tableau and run the views!
# ------------------------------------------------------------------------------
dte = dt.date.today().strftime('%m%d')
file_name = "student_enrollment_{}.csv".format(dte)
std_enrol.to_csv(file_name, index=False)
