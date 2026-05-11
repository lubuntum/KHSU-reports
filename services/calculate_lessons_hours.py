import json
from io import BytesIO

import pandas as pd
from collections import defaultdict
from pathlib import Path
def calculate_lessons_hours(data, teacher, month):
    # Dictionary to store counts
    lesson_counts = defaultdict(int)
    # Extract lessons from all weeks
    for week in data:
        if 'days' in week:
            for day in week['days']:
                if 'lessons' in day and day['lessons'] is not None:
                    for lesson in day['lessons']:
                        if lesson is not None:
                            subject = lesson.get('subject', '')
                            groups = lesson.get('group', [])
                            type_lesson = lesson.get('type_lesson', '')

                            # Handle multiple groups
                            for group in groups:
                                key = (subject, group, type_lesson)
                                lesson_counts[key] += 1
    # Prepare data for DataFrame
    rows = []
    for (subject, group, type_lesson), count in lesson_counts.items():
        academic_hours = count * 2
        rows.append({
            'Subject': subject,
            'Group': group,
            'Type of Lesson': type_lesson,
            'Count': count,
            'Academic Hours (Count * 2)': academic_hours
        })

    # Create DataFrame
    df = pd.DataFrame(rows)
    # Sort by Subject, then Group, then Type of Lesson
    if not df.empty:
        df = df.sort_values(['Subject', 'Group', 'Type of Lesson']).reset_index(drop=True)
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Lessons Summary', index=False)

        # Adjust column widths
        worksheet = writer.sheets['Lessons Summary']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)
        return output