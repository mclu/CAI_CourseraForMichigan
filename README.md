# Coursera for Michigan - Data Cleaning Script

*Author: Ming-Chen (Amy) Lu (mingchlu@umich.edu)*
*Date: June 23, 2020*

## Input files: 
- student_term_with_descriptions_hashed.csv
- coursera_enrollment_hashed.csv
- term.csv, coursera_course.csv
- coursera_specialization.csv
- coursera_specializationcourses.csv

## Output file: student_enrollment_{date}.csv

## Description
The script combines UM student term information and enrollments on Coursera for Michigan so that the combined data can be used for the visualizations on Tableau. The major data cleaning steps are described as follows:

1. Students who weren't registered or withdraw were removed and the remainings were filtered by their lastet term.

2. The course names and the specialization names were added into the coursera enrollment file. Two columns indicating whether or not a student had completed the course and whether or not a student was an alumnus were also added.

3. Data from 1 and 2 was merged by username. One final cleanup was randomly dropped one of the careers when an user had two.

The data is then exported with the name "student_enrollment" and the current date. Noted that the input file names should be the same as mentioned above.
